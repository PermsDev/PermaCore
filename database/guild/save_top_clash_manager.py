from datetime import date
from database.database import get_guild_pool as get_pool

# =========================================================
# SAVE TOP CLASH
# =========================================================

async def save_top_clash(
    growids: list[str],
    user_ids: list[int | None]
):
    """
    Menyimpan Top 5 Event Clash.

    Proses:
    1. Menentukan Series berdasarkan tanggal hari ini.
    2. Membuat Series jika belum tersedia.
    3. Memastikan Series tersebut active.
    4. Mencari atau membuat Event Clash bulan tersebut.
    5. Mengupdate / menambahkan hasil Top 1-5.
    """

    if len(growids) != 5:
        raise ValueError("Jumlah GrowID harus tepat 5.")

    if len(user_ids) != 5:
        raise ValueError("Jumlah user_id harus tepat 5.")

    today = date.today()

    pool = get_pool()

    async with pool.acquire() as conn:

        try:
            async with conn.cursor() as cursor:

                # =================================================
                # 1. TENTUKAN PERIODE SERIES
                # =================================================

                if today.month >= 7:
                    series_start = date(today.year, 7, 1)
                    series_end = date(today.year + 1, 6, 30)
                else:
                    series_start = date(today.year - 1, 7, 1)
                    series_end = date(today.year, 6, 30)

                # =================================================
                # 2. CARI SERIES
                # =================================================

                await cursor.execute(
                    """
                    SELECT
                        series_id,
                        series_name,
                        start_date,
                        end_date,
                        status
                    FROM event_clash_series
                    WHERE start_date <= %s
                        AND end_date >= %s
                    LIMIT 1
                    """,
                    (
                        today,
                        today,
                    )
                )

                series = await cursor.fetchone()

                # =================================================
                # 3. BUAT SERIES JIKA BELUM ADA
                # =================================================

                if series is None:

                    await cursor.execute(
                        """
                        SELECT
                            series_id,
                            series_name
                        FROM event_clash_series
                        ORDER BY series_id DESC
                        LIMIT 1
                        """
                    )

                    last_series = await cursor.fetchone()

                    if last_series:
                        last_series_name = last_series[1]

                        try:
                            last_number = int(
                                last_series_name.replace(
                                    "Series ",
                                    ""
                                )
                            )
                        except ValueError:
                            last_number = last_series[0]

                        next_number = last_number + 1

                    else:
                        next_number = 1

                    series_name = f"Series {next_number}"

                    await cursor.execute(
                        """
                        INSERT INTO event_clash_series (
                            series_name,
                            start_date,
                            end_date,
                            status
                        )
                        VALUES (%s, %s, %s, 'active')
                        """,
                        (
                            series_name,
                            series_start,
                            series_end,
                        )
                    )

                    series_id = cursor.lastrowid

                else:
                    series_id = series[0]

                # =================================================
                # 4. PASTIKAN HANYA SERIES INI YANG ACTIVE
                # =================================================

                await cursor.execute(
                    """
                    UPDATE event_clash_series
                    SET status = 'finished'
                    WHERE status = 'active'
                        AND series_id != %s
                    """,
                    (
                        series_id,
                    )
                )

                await cursor.execute(
                    """
                    UPDATE event_clash_series
                    SET status = 'finished'
                    WHERE end_date < %s
                        AND series_id != %s
                    """,
                    (
                        today,
                        series_id,
                    )
                )

                await cursor.execute(
                    """
                    UPDATE event_clash_series
                    SET status = 'active'
                    WHERE series_id = %s
                    """,
                    (
                        series_id,
                    )
                )

                # =================================================
                # 5. CARI CLASH BULAN INI
                # =================================================

                clash_month = today.month
                clash_year = today.year

                await cursor.execute(
                    """
                    SELECT
                        clash_id
                    FROM event_clash
                    WHERE series_id = %s
                        AND clash_month = %s
                        AND clash_year = %s
                    LIMIT 1
                    """,
                    (
                        series_id,
                        clash_month,
                        clash_year,
                    )
                )

                clash = await cursor.fetchone()

                # =================================================
                # 6. BUAT CLASH JIKA BELUM ADA
                # =================================================

                if clash is None:

                    await cursor.execute(
                        """
                        INSERT INTO event_clash (
                            series_id,
                            clash_month,
                            clash_year,
                            event_date
                        )
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            series_id,
                            clash_month,
                            clash_year,
                            today,
                        )
                    )

                    clash_id = cursor.lastrowid

                else:

                    clash_id = clash[0]

                    # event_date mengikuti tanggal input terbaru
                    await cursor.execute(
                        """
                        UPDATE event_clash
                        SET event_date = %s
                        WHERE clash_id = %s
                        """,
                        (
                            today,
                            clash_id,
                        )
                    )

                # =================================================
                # 7. AMBIL RESULT YANG SUDAH ADA
                # =================================================

                await cursor.execute(
                    """
                    SELECT
                        result_id,
                        rank_position
                    FROM event_clash_result
                    WHERE clash_id = %s
                    """,
                    (
                        clash_id,
                    )
                )

                existing_results = await cursor.fetchall()

                existing_by_rank = {
                    row[1]: row[0]
                    for row in existing_results
                }

                # =================================================
                # 8. KOSONGKAN USER_ID TERLEBIH DAHULU
                # =================================================
                #
                # Ini penting karena:
                #
                # Top 1 A
                # Top 2 B
                #
                # bisa berubah menjadi:
                #
                # Top 1 B
                # Top 2 A
                #
                # Jika langsung UPDATE, UNIQUE(clash_id,user_id)
                # bisa terkena duplicate.
                #
                # NULL diperbolehkan oleh database dan FK tetap valid.
                #

                await cursor.execute(
                    """
                    UPDATE event_clash_result
                    SET
                        user_id = NULL,
                        growid = NULL
                    WHERE clash_id = %s
                    """,
                    (
                        clash_id,
                    )
                )

                # =================================================
                # 9. UPDATE / INSERT TOP 1-5
                # =================================================

                for index in range(5):

                    rank_position = index + 1

                    user_id = user_ids[index]
                    growid = growids[index]

                    if user_id is not None:
                        saved_user_id = user_id
                        saved_growid = None
                    else:
                        saved_user_id = None
                        saved_growid = growid

                    # ---------------------------------------------
                    # RESULT SUDAH ADA
                    # ---------------------------------------------

                    if rank_position in existing_by_rank:

                        result_id = existing_by_rank[
                            rank_position
                        ]

                        await cursor.execute(
                            """
                            UPDATE event_clash_result
                            SET
                                user_id = %s,
                                growid = %s
                            WHERE result_id = %s
                            """,
                            (
                                saved_user_id,
                                saved_growid,
                                result_id,
                            )
                        )

                    # ---------------------------------------------
                    # RESULT BELUM ADA
                    # ---------------------------------------------

                    else:

                        await cursor.execute(
                            """
                            INSERT INTO event_clash_result (
                                clash_id,
                                user_id,
                                growid,
                                rank_position
                            )
                            VALUES (%s, %s, %s, %s)
                            """,
                            (
                                clash_id,
                                saved_user_id,
                                saved_growid,
                                rank_position,
                            )
                        )

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise

    return {
        "series_id": series_id,
        "clash_id": clash_id,
        "event_date": today,
    }