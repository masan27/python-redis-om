from typing import Any, List, Optional, Tuple
from loguru import logger
from app.models import MODEL_REGISTRY
from app.schemas.query import FilterItem

def build_condition(model, field_name: str, op: str, value: Any):
    """
    Builds a redis-om query expression for a given field and operator.
    Supports dot-notation for nested fields.
    """
    field_parts = field_name.split(".")
    field_obj = model
    
    for part in field_parts:
        try:
            field_obj = getattr(field_obj, part)
        except AttributeError:
            logger.error(f"Field '{part}' not found on model {field_obj}")
            raise ValueError(f"Field '{field_name}' is invalid for model {model.__name__}")

    # Operator mapping
    if op == "in":
        if not isinstance(value, list) or not value:
            raise ValueError("Operator 'in' requires a non-empty list")
        cond = (field_obj == value[0])
        for v in value[1:]:
            cond |= (field_obj == v)
        return cond
    
    if op == "between":
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError("Operator 'between' requires a list with 2 values")
        return (field_obj >= value[0]) & (field_obj <= value[1])

    if op == "!in":
        if not isinstance(value, list) or not value:
            raise ValueError("Operator '!in' requires a non-empty list")
        cond = (field_obj != value[0])
        for v in value[1:]:
            cond &= (field_obj != v)
        return cond

    ops = {
        "==": field_obj == value,
        "!=": field_obj != value,
        ">":  field_obj > value,
        "<":  field_obj < value,
        ">=": field_obj >= value,
        "<=": field_obj <= value,
        "contains":   field_obj % f"*{value}*",
        "like":       field_obj % f"*{value}*", # Alias
        "startswith": field_obj ^ value,
        "endswith":   field_obj % f"*{value}",
        "null":       field_obj == None,
        "not_null":   field_obj != None,
    }
    
    if op not in ops:
        raise ValueError(f"Operator '{op}' is not supported")
        
    return ops[op]

def execute_query(
    model_name: str,
    filters: Optional[List[FilterItem]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_asc: bool = True,
    fields: Optional[List[str]] = None,
) -> Tuple[List[dict], int]:
    """
    Executes a dynamic query against a registered Redis OM model.
    """
    if model_name not in MODEL_REGISTRY:
        raise KeyError(f"Model '{model_name}' is not registered")

    model = MODEL_REGISTRY[model_name]
    
    try:
        # Build query
        if filters:
            conditions = [build_condition(model, f.field, f.op, f.value) for f in filters]
            query = model.find(*conditions)
        else:
            query = model.find()

        # Sort
        if sort_by:
            sort_field = f"-{sort_by}" if not sort_asc else sort_by
            query = query.sort_by(sort_field)

        # Count total
        try:
            total = query.count()
        except Exception:
            logger.warning(f"Failed to get count for query on {model_name}")
            total = 0

        # Pagination & Execution
        start = offset or 0
        if limit is not None:
            results = query[start : start + limit]
        else:
            results = query.all()
            if start > 0:
                results = results[start:]

        # Transform to dict
        docs = []
        for r in results:
            data = r.model_dump() if hasattr(r, "model_dump") else r.dict()
            
            # Internal field cleanup
            data.pop("update_time", None) 
            
            if fields:
                data = {k: v for k, v in data.items() if k in fields}
            docs.append(data)

        return docs, total

    except Exception as e:
        logger.exception(f"Error executing query for {model_name}: {e}")
        raise
