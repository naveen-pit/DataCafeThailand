SELECT
T4.host1,
T4.host2,
T4.nintersect,
T6.cnt as cnt1,
T7.cnt as cnt2,
T6.cnt+T7.cnt-T4.nintersect AS nunion
FROM (
	SELECT
	T3.host1 AS host1,
	T3.host2 AS host2,
	COUNT(userid) AS nintersect
	FROM (
		SELECT
		DISTINCT
		CASE
		WHEN T1.hostid > T2.hostid THEN T1.hostid
		ELSE T2.hostid
		END AS host1,
		CASE
		WHEN T1.hostid > T2.hostid THEN T2.hostid
		ELSE T1.hostid
		END AS host2,
		T1.userid AS userid
		FROM (
			SELECT
			a.user_id AS userid,
			b.host_user_id AS hostid
			FROM
			`datacafethailand.social_insight.activity_feed` AS a
			INNER JOIN
			`datacafethailand.social_insight.host_x_txn` AS b
			ON
			a.key_id = b.key_id
			AND a.source=b.source
			UNION ALL
			SELECT
			a.user_id AS userid,
			b.host_user_id AS hostid
			FROM
			`datacafethailand.social_insight.raw_feed` AS a
			INNER JOIN
			`datacafethailand.social_insight.host_x_txn` AS b
			ON
			a.key_id = b.key_id
			AND a.source=b.source ) AS T1
			INNER JOIN (
				SELECT
				a.user_id AS userid,
				b.host_user_id AS hostid
				FROM
				`datacafethailand.social_insight.activity_feed` AS a
				INNER JOIN
				`datacafethailand.social_insight.host_x_txn` AS b
				ON
				a.key_id = b.key_id
				AND a.source=b.source
				UNION ALL
				SELECT
				a.user_id AS userid,
				b.host_user_id AS hostid
				FROM
				`datacafethailand.social_insight.raw_feed` AS a
				INNER JOIN
				`datacafethailand.social_insight.host_x_txn` AS b
				ON
				a.key_id = b.key_id
				AND a.source=b.source ) AS T2
			ON T1.userid=T2.userid ) T3
		GROUP BY 1,2 ) T4
	LEFT OUTER JOIN (
		SELECT
		T5.hostid,
		COUNT(distinct T5.userid) AS cnt
		FROM (
			SELECT
			a.user_id AS userid,
			b.host_user_id AS hostid
			FROM
			`datacafethailand.social_insight.activity_feed` AS a
			INNER JOIN
			`datacafethailand.social_insight.host_x_txn` AS b
			ON
			a.key_id = b.key_id
			AND a.source=b.source
			UNION ALL
			SELECT
			a.user_id AS userid,
			b.host_user_id AS hostid
			FROM
			`datacafethailand.social_insight.raw_feed` AS a
			INNER JOIN
			`datacafethailand.social_insight.host_x_txn` AS b
			ON
			a.key_id = b.key_id
			AND a.source=b.source) T5
			GROUP BY
			1 ) T6
ON
T4.host1=T6.hostid
LEFT OUTER JOIN (
	SELECT
	T5.hostid,
	COUNT(distinct T5.userid) AS cnt
	FROM (
		SELECT
		a.user_id AS userid,
		b.host_user_id AS hostid
		FROM
		`datacafethailand.social_insight.activity_feed` AS a
		INNER JOIN
		`datacafethailand.social_insight.host_x_txn` AS b
		ON
		a.key_id = b.key_id
		AND a.source=b.source
		UNION ALL
		SELECT
		a.user_id AS userid,
		b.host_user_id AS hostid
		FROM
		`datacafethailand.social_insight.raw_feed` AS a
		INNER JOIN
		`datacafethailand.social_insight.host_x_txn` AS b
		ON
		a.key_id = b.key_id
		AND a.source=b.source) T5
		GROUP BY
		1 ) T7
ON
T4.host2=T7.hostid