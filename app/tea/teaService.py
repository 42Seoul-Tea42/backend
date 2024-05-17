from ..db.db import PostgreSQLFactory
from ..utils.const import (
    MAX_SUGGEST,
    AGE_GAP,
    Gender,
    AREA_DISTANCE,
    MIN_AGE,
    StatusCode,
    Authorization,
)
import app.user.userUtils as userUtils
from psycopg2.extras import DictCursor
from werkzeug.exceptions import Unauthorized


def suggest(id):
    # 유저 API 접근 권한 확인
    userUtils.check_authorization(id, Authorization.EMOJI)

    # 성적 취향이 서로 맞고
    # 싫은게 하나도 없고 (hate_tag, hate_emoji)
    # 겹치는거 많은 순(tag, emoji)
    # 유저와 같은 지역에 fame rating 높은 사람으로

    user = userUtils.get_user(id)
    if user is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")

    tags, hate_tags = user["tags"], user["hate_tags"]
    emoji, hate_emoji = user["emoji"], user["hate_emoji"]
    long, lat = user["longitude"], user["latitude"]
    similar = user["similar"]

    if MIN_AGE <= user["age"]:
        min_age = max(user["age"] - AGE_GAP, MIN_AGE)
        max_age = user["age"] + AGE_GAP
    else:
        min_age = max_age = MIN_AGE

    find_taste = user["gender"] | Gender.OTHER
    find_gender = Gender.ALL if user["taste"] & Gender.OTHER else user["taste"]

    db_data = []
    conn = PostgreSQLFactory.get_connection()

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT * FROM ( \
                            SELECT *, \
                                sqrt((longitude - %s)^2 + (latitude - %s)^2) AS distance \
                            FROM "User" \
                        ) AS user_distance \
                WHERE "id" != %s \
                    AND "id" NOT IN ( \
                            SELECT "target_id" \
                            FROM "Block" \
                            WHERE "user_id" = %s ) \
                    AND "id" NOT IN ( \
                            SELECT "user_id" \
                            FROM "Block" \
                            WHERE "target_id" = %s ) \
                    AND "age" BETWEEN %s AND %s \
                    AND "emoji" IS NOT NULL \
                    AND "taste" & %s > 0 \
                    AND "gender" & %s > 0 \
                    AND "hate_tags" & %s = 0 \
                    AND "tags" & %s = 0 \
                    AND "hate_emoji" & %s = 0 \
                    AND "emoji" & %s = 0 \
                    AND "tags" & %s > 0 \
                    AND CASE WHEN %s THEN "emoji" & %s > 0 \
                            ELSE "emoji" & %s = 0 \
                        END \
                    AND "distance" <= %s \
                ORDER BY CASE WHEN %s THEN "emoji" & %s \
                        END DESC, \
                        distance ASC, \
                        "count_fancy"::float / COALESCE("count_view", 1) DESC \
                LIMIT %s ;'

        cursor.execute(
            sql,
            (
                long,
                lat,
                id,
                id,
                id,
                min_age,
                max_age,
                find_taste,
                find_gender,
                tags,
                hate_tags,
                emoji,
                hate_emoji,
                tags,
                similar,
                emoji,
                emoji,
                AREA_DISTANCE,
                similar,
                emoji,
                MAX_SUGGEST,
            ),
        )
        db_data = cursor.fetchall()

        result = [userUtils.get_profile(id, target["id"]) for target in db_data]
        return {
            "profiles": result,
        }, StatusCode.OK
