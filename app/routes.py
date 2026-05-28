from datetime import datetime

from flask import Blueprint, request, jsonify
from app.db import get_db, release_db
from flasgger import swag_from

stats_bp = Blueprint("stats", __name__)

SELECT_ALL_SQL = "SELECT * FROM farm_stats;"
SELECT_ONE_SQL = "SELECT * FROM farm_stats WHERE id = %s;"
DELETE_SQL = "DELETE FROM farm_stats WHERE id = %s;"


@stats_bp.route("/stats", methods=["GET"])
@swag_from({"responses": {200: {"description": "List of all stats"}}})
def get_all_stats():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_ALL_SQL)
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            return jsonify([dict(zip(colnames, row)) for row in rows])
    finally:
        release_db(conn)


@stats_bp.route("/stats/<int:stat_id>", methods=["GET"])
@swag_from({
    'parameters': [
        {'name': 'stat_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        '200': {'description': 'Stat found'},
        '404': {'description': 'Not found'}
    }
})
def get_one_stat(stat_id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_ONE_SQL, (stat_id,))
            row = cur.fetchone()
            if not row:
                return jsonify({"error": "Not found"}), 404
            colnames = [desc[0] for desc in cur.description]
            return jsonify(dict(zip(colnames, row)))
    finally:
        release_db(conn)


@stats_bp.route("/stats", methods=["POST"])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'farm': {'type': 'string', 'example': 'Ферма 1'},
                    'date': {'type': 'string', 'example': 'Mon, 23 Mar 2026 00:00:00 GMT'},
                    'abort': {'type': 'integer', 'example': 0},
                    'bulls_from_cows': {'type': 'integer', 'example': 0}
                },
                'required': ['farm', 'date']
            }
        }
    ],
    'responses': {
        '201': {'description': 'Created'},
        '400': {'description': 'Validation error'}
    }
})
def create_stat():
    data = request.json or {}

    if not data.get("farm") or not data.get("date"):
        return jsonify({"error": "farm and date are required"}), 400

    parsed_date = parse_date(data.get("date"))
    if not parsed_date:
        return jsonify({"error": "Invalid date format. Use 'Mon, 23 Mar 2026 00:00:00 GMT'"}), 400
    
    conn = get_db()
    try:
        with conn.cursor() as cur:
            query = """
                INSERT INTO farm_stats (
                    farm, date, abort, bulls_from_cows, bulls_from_heifers,
                    conception_cows, conception_heifers, cows_from_cows, cows_from_heifers,
                    dead_bulls, dead_heifers, preg_rate_cows, preg_rate_heifers,
                    reproduction_cows, reproduction_heifers
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """
            values = (
                data.get("farm"),
                parsed_date,
                data.get("abort", 0),
                data.get("bulls_from_cows", 0),
                data.get("bulls_from_heifers", 0),
                data.get("conception_cows", 0),
                data.get("conception_heifers", 0),
                data.get("cows_from_cows", 0),
                data.get("cows_from_heifers", 0),
                data.get("dead_bulls", 0),
                data.get("dead_heifers", 0),
                data.get("preg_rate_cows", 0.0),
                data.get("preg_rate_heifers", 0.0),
                data.get("reproduction_cows", 0),
                data.get("reproduction_heifers", 0),
            )
            cur.execute(query, values)
            new_id = cur.fetchone()[0]
            conn.commit()
        return jsonify({"id": new_id, "message": "Created"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        release_db(conn)


@stats_bp.route("/stats/<int:stat_id>", methods=["PUT"])
@swag_from({
    'parameters': [
        {'name': 'stat_id', 'in': 'path', 'type': 'integer', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'farm': {'type': 'string', 'example': 'Ферма 1'},
                    'date': {'type': 'string', 'example': 'Mon, 23 Mar 2026 00:00:00 GMT'},
                    'abort': {'type': 'integer', 'example': 0}
                },
                'required': ['farm', 'date']
            }
        }
    ],
    'responses': {
        '200': {'description': 'Updated'},
        '404': {'description': 'Not found'}
    }
})
def update_stat(stat_id):
    data = request.json or {}

    if not data.get("farm") or not data.get("date"):
        return jsonify({"error": "farm and date are required"}), 400

    parsed_date = parse_date(data.get("date"))
    if not parsed_date:
        return jsonify({"error": "Invalid date format. Use 'Mon, 23 Mar 2026 00:00:00 GMT'"}), 400

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_ONE_SQL, (stat_id,))
            if not cur.fetchone():
                return jsonify({"error": "Not found"}), 404

            query = """
                UPDATE farm_stats SET
                    farm = %s, date = %s, abort = %s, bulls_from_cows = %s, bulls_from_heifers = %s,
                    conception_cows = %s, conception_heifers = %s, cows_from_cows = %s, cows_from_heifers = %s,
                    dead_bulls = %s, dead_heifers = %s, preg_rate_cows = %s, preg_rate_heifers = %s,
                    reproduction_cows = %s, reproduction_heifers = %s
                WHERE id = %s;
            """
            values = (
                data.get("farm"),
                parsed_date,
                data.get("abort", 0),
                data.get("bulls_from_cows", 0),
                data.get("bulls_from_heifers", 0),
                data.get("conception_cows", 0),
                data.get("conception_heifers", 0),
                data.get("cows_from_cows", 0),
                data.get("cows_from_heifers", 0),
                data.get("dead_bulls", 0),
                data.get("dead_heifers", 0),
                data.get("preg_rate_cows", 0.0),
                data.get("preg_rate_heifers", 0.0),
                data.get("reproduction_cows", 0),
                data.get("reproduction_heifers", 0),
                stat_id,
            )
            cur.execute(query, values)
            conn.commit()
        return jsonify({"message": "Updated successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        release_db(conn)


@stats_bp.route("/stats/<int:stat_id>", methods=["PATCH"])
@swag_from({
    'parameters': [
        {'name': 'stat_id', 'in': 'path', 'type': 'integer', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'farm': {'type': 'string'},
                    'date': {'type': 'string', 'example': 'Mon, 23 Mar 2026 00:00:00 GMT'},
                    'abort': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        '200': {'description': 'Updated'},
        '404': {'description': 'Not found'}
    }
})
def patch_stat(stat_id):
    data = request.json or {}
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_ONE_SQL, (stat_id,))
            row = cur.fetchone()
            if not row:
                return jsonify({"error": "Not found"}), 404

            colnames = [desc[0] for desc in cur.description]
            current = dict(zip(colnames, row))

            for key, value in data.items():
                if key in current and key != "id":
                    if key == "date":
                        parsed = parse_date(value)
                        if parsed:
                            current[key] = parsed
                    else:
                        current[key] = value
            query = """
                UPDATE farm_stats SET
                    farm = %s, date = %s, abort = %s, bulls_from_cows = %s, bulls_from_heifers = %s,
                    conception_cows = %s, conception_heifers = %s, cows_from_cows = %s, cows_from_heifers = %s,
                    dead_bulls = %s, dead_heifers = %s, preg_rate_cows = %s, preg_rate_heifers = %s,
                    reproduction_cows = %s, reproduction_heifers = %s
                WHERE id = %s;
            """
            values = (
                current["farm"],
                current["date"],
                current["abort"],
                current["bulls_from_cows"],
                current["bulls_from_heifers"],
                current["conception_cows"],
                current["conception_heifers"],
                current["cows_from_cows"],
                current["cows_from_heifers"],
                current["dead_bulls"],
                current["dead_heifers"],
                current["preg_rate_cows"],
                current["preg_rate_heifers"],
                current["reproduction_cows"],
                current["reproduction_heifers"],
                stat_id
            )
            cur.execute(query, values)
            conn.commit()
        return jsonify({"message": "Updated successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        release_db(conn)


@stats_bp.route("/stats/<int:stat_id>", methods=["DELETE"])
@swag_from({
    'parameters': [
        {'name': 'stat_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        '200': {'description': 'Deleted'},
        '404': {'description': 'Not found'}
    }
})
def delete_stat(stat_id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(DELETE_SQL, (stat_id,))
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({"error": "Not found"}), 404
            return jsonify({"message": "Deleted"}), 200
    finally:
        release_db(conn)


def parse_date(date_value):
    if not date_value:
        return None

    if isinstance(date_value, str):
        for fmt in ("%Y-%m-%d", "%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(date_value, fmt).date()
            except Exception as e:
                continue
    return None
