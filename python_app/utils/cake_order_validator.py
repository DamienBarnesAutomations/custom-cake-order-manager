import json
import copy
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_option_data(field_key, value, config):
    if value in [None, "", []]:
        return {"value": None, "rank": -1}
    
    settings = config.get(field_key, {})
    val_str = str(value).lower()
    
    try:
        numeric_filter = "".join(c for c in val_str if c.isdigit() or c == '.')
        if numeric_filter:
            return {"value": value, "rank": float(numeric_filter)}
    except (ValueError, TypeError) as e:
        logger.debug(f"Could not parse numeric rank for {field_key}: {e}")

    options = [opt.lower() for opt in settings.get("options", [])]
    try:
        index = options.index(val_str)
        return {"value": value, "rank": index + 100}
    except ValueError:
        return {"value": value, "rank": -1}

def validate_rules(field_key, value, rules, context, config, tier_index=None):
    if value in [None, ""]:
        return None
    
    settings = config.get(field_key, {})
    
    # 1. Menu Option Validation
    if settings.get("options"):
        options_lower = [opt.lower() for opt in settings["options"]]
        if str(value).lower() not in options_lower:
            opts_str = ", ".join(settings["options"])
            return f"Sorry, '{value}' is not on our menu for {settings.get('display_name')}. Options: {opts_str}."

    # 2. Iterative Rule Processing
    for rule in rules:
        rule_type = rule.get("type")
        rule_config = rule.get("config", {})

        try:
            if rule_type == 'min_base_for_tiers':
                current_tiers = int(context.get("tiers", 0))
                if current_tiers >= rule_config.get("tiers", 0) and tier_index == 0:
                    size_rank = get_option_data(field_key, value, config)["rank"]
                    if size_rank < rule_config.get("min_inches", 0):
                        return rule.get("error_message")

            elif rule_type == 'lead_time':
                selected_date = datetime.fromisoformat(str(value).replace('Z', ''))
                min_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                min_date += timedelta(days=rule_config.get("min_days", 0))
                if selected_date < min_date:
                    return rule.get("error_message")

            elif rule_type == 'max_length':
                if len(str(value)) > rule_config.get("max_chars", 999):
                    return f"The note is too long. Max {rule_config['max_chars']} characters."

            elif rule_type == 'min_value':
                try:
                    if int(value) < rule_config.get("min", 0):
                        return rule.get("error_message")
                except (ValueError, TypeError):
                    return "Please provide a valid number for the quantity."

            elif rule_type == 'multiple_of':
                try:
                    if int(value) % rule_config.get("factor", 1) != 0:
                        return rule.get("error_message")
                except (ValueError, TypeError):
                    return f"Quantity must be a multiple of {rule_config.get('factor')}."

        except Exception as e:
            logger.error(f"Error executing rule {rule_type} on {field_key}: {e}")
            return "Internal validation error occurred."

    # 3. Tier Hierarchy Validation
    if field_key == 'size' and tier_index is not None and tier_index > 0:
        current_size_rank = get_option_data('size', value, config)["rank"]
        tier_defs = context.get("tier_definitions", [])
        
        if tier_index < len(tier_defs):
            below_tier = tier_defs[tier_index - 1]
            size_below_rank = get_option_data('size', below_tier.get("size"), config)["rank"]
            
            if size_below_rank != -1 and current_size_rank >= size_below_rank:
                return f"Tier {tier_index + 1} must be smaller than Tier {tier_index} ({below_tier.get('size')}\")."

    return None

def validate_cake_order(old_selection, new_extraction, config):
    logger.info("Starting cake order validation...")
    
    validated_state = copy.deepcopy(old_selection or {})
    error_items = {}
    missing_items = {}
    new_data = {}

    # --- 0. Process order_type first ---
    # Must be in validated_state before the global loop runs so that
    # dependency checks on tiers/num_cupcakes resolve correctly.
    order_type_settings = config.get("order_type", {})
    new_order_type = new_extraction.get("order_type")
    if new_order_type not in [None, ""]:
        if new_order_type != old_selection.get("order_type"):
            new_data["order_type"] = new_order_type
        validated_state["order_type"] = new_order_type
    elif validated_state.get("order_type") in [None, ""]:
        if order_type_settings:
            missing_items["order_type"] = order_type_settings

    # --- 1. Process Global Fields ---
    for field_key, settings in config.items():
        if settings.get("scope") != 'global':
            continue

        # Already handled above
        if field_key == 'order_type':
            continue

        new_val = new_extraction.get(field_key)
        is_new_provided = new_val not in [None, ""]
        
        if is_new_provided and new_val != old_selection.get(field_key):
            new_data[field_key] = new_val

        value_to_validate = new_val if is_new_provided else validated_state.get(field_key)

        dep_rule = next((r for r in settings.get("rules", []) if r["type"] == "dependency"), None)
        
        if dep_rule:
            parent_val = validated_state.get(dep_rule["config"]["depends_on"])
            if parent_val != dep_rule["config"]["value"]:
                # Dependency not met — skip field entirely, don't add to missing
                continue
            elif not value_to_validate:
                # Dependency met but value not provided — add to missing
                missing_items[field_key] = settings
                continue

        rule_error = validate_rules(field_key, value_to_validate, settings.get("rules", []), validated_state, config)

        if value_to_validate not in [None, ""]:
            if rule_error:
                error_items[field_key] = rule_error
            else:
                validated_state[field_key] = value_to_validate
        elif settings.get("is_required") is not False:
            missing_items[field_key] = settings

    # --- 2. Order-type branching ---
    order_type = validated_state.get("order_type")

    if order_type == 'cake':
        # --- 2a. Sync Tier Definitions ---
        try:
            target_tier_count = int(validated_state.get("tiers", 0))
        except (ValueError, TypeError):
            logger.warning("Invalid tier count provided; defaulting to 0.")
            target_tier_count = 0

        if "tier_definitions" not in validated_state:
            validated_state["tier_definitions"] = []
        
        current_tiers = validated_state["tier_definitions"]
        if len(current_tiers) < target_tier_count:
            for i in range(len(current_tiers), target_tier_count):
                current_tiers.append({"tier_index": i + 1, "size": None, "flavor": None, "layers": None})
        else:
            validated_state["tier_definitions"] = current_tiers[:target_tier_count]

        # --- 2b. Process Tier Scope Fields ---
        for idx, tier in enumerate(validated_state["tier_definitions"]):
            ai_tiers_list = new_extraction.get("tier_definitions", []) or []
            ai_tier = ai_tiers_list[idx] if idx < len(ai_tiers_list) else {}
            
            old_tiers_list = old_selection.get("tier_definitions", []) or []
            old_tier = old_tiers_list[idx] if idx < len(old_tiers_list) else {}

            for field_key, settings in config.items():
                if settings.get("scope") != 'tier':
                    continue

                new_val = ai_tier.get(field_key)
                is_new_provided = new_val not in [None, ""]

                if is_new_provided and new_val != old_tier.get(field_key):
                    if "tier_definitions" not in new_data:
                        new_data["tier_definitions"] = {}
                    if idx not in new_data["tier_definitions"]:
                        new_data["tier_definitions"][idx] = {"tier_index": idx + 1}
                    new_data["tier_definitions"][idx][field_key] = new_val

                value_to_validate = new_val if is_new_provided else tier.get(field_key)
                rule_error = validate_rules(field_key, value_to_validate, settings.get("rules", []), validated_state, config, idx)

                if value_to_validate not in [None, ""]:
                    if rule_error:
                        error_items[f"tier_{idx + 1}_{field_key}"] = rule_error
                    else:
                        tier[field_key] = value_to_validate
                else:
                    display_name = f"Tier {idx + 1} {settings.get('display_name')}"
                    tier_settings = {**settings, "display_name": display_name}

                    if field_key == 'size' and idx > 0:
                        below_size = validated_state["tier_definitions"][idx - 1].get("size")
                        if below_size:
                            try:
                                below_rank = float("".join(c for c in str(below_size) if c.isdigit() or c == '.'))
                                filtered_options = [
                                    opt for opt in settings.get("options", [])
                                    if float("".join(c for c in str(opt) if c.isdigit() or c == '.') or "999") < below_rank
                                ]
                                tier_settings = {**tier_settings, "options": filtered_options}
                            except (ValueError, TypeError):
                                pass

                    missing_items[f"tier_{idx + 1}_{field_key}"] = tier_settings

    elif order_type == 'cupcakes':
        # --- 2c. Sync Cupcake Definition ---
        if "cupcake_definition" not in validated_state or validated_state["cupcake_definition"] is None:
            validated_state["cupcake_definition"] = {}
        
        cupcake = validated_state["cupcake_definition"]
        ai_cupcake = new_extraction.get("cupcake_definition", {}) or {}
        old_cupcake = old_selection.get("cupcake_definition", {}) or {}

        for field_key, settings in config.items():
            if settings.get("scope") != 'cupcake':
                continue

            new_val = ai_cupcake.get(field_key)
            is_new_provided = new_val not in [None, ""]

            if is_new_provided and new_val != old_cupcake.get(field_key):
                if "cupcake_definition" not in new_data:
                    new_data["cupcake_definition"] = {}
                new_data["cupcake_definition"][field_key] = new_val

            value_to_validate = new_val if is_new_provided else cupcake.get(field_key)

            rule_error = validate_rules(field_key, value_to_validate, settings.get("rules", []), validated_state, config)

            if value_to_validate not in [None, ""]:
                if rule_error:
                    error_items[field_key] = rule_error
                else:
                    cupcake[field_key] = value_to_validate
            elif settings.get("is_required") is not False:
                missing_items[field_key] = settings

    logger.info(f"Validation complete. Complete: {not (error_items or missing_items)}")

    sorted_missing = dict(
        sorted(
            missing_items.items(),
            key=lambda x: x[1].get("sort_order", 999)
        )
    )

    return {
        "updated_state": validated_state,
        "new_data": new_data,
        "has_errors": len(error_items) > 0,
        "errors": error_items,
        "has_missing_data": len(missing_items) > 0,
        "missing": sorted_missing,
        "is_complete": len(error_items) == 0 and len(missing_items) == 0
    }