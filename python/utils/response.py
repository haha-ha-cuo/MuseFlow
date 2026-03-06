from flask import jsonify

def success(data=None, msg="success", code=200, **kwargs):
    """
    统一成功响应
    """
    response = {
        "code": code,
        "msg": msg,
        "data": data
    }
    # 允许传入额外的字段 (如 title, description 等，兼容旧接口)
    if kwargs:
        response.update(kwargs)
    return jsonify(response), code

def error(msg="error", code=400, **kwargs):
    """
    统一错误响应
    """
    response = {
        "code": code,
        "msg": msg
    }
    if kwargs:
        response.update(kwargs)
    return jsonify(response), code