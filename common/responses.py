from flask import jsonify, request

def ok(data=None, meta=None, status=200):
    return jsonify({"data": data or {}, "meta": meta or {"path": request.path}}), status
