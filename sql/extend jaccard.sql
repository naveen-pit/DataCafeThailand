/*	activity_feed 	userA like postA
	host_x_txn 		page A post postA
	raw_feed 		user A comment postA
*/
SELECT T4.host1,
       T4.host2,
       T4.nintersect,
       T4.nunion,
	   T4.postmonth
FROM
  ( SELECT T3.host1 AS host1,
           T3.host2 AS host2,
           SUM(CASE WHEN freq2<freq1 THEN freq2 ELSE freq1 END) AS nintersect,
           SUM(CASE WHEN freq2 <= freq1 THEN freq1 ELSE freq2 END) AS nunion,
		   T3.postmonth
		   
   FROM
     ( SELECT DISTINCT CASE
                           WHEN T1.hostid > T2.hostid THEN T1.hostid
                           ELSE T2.hostid
                       END AS host1,
                       CASE
                           WHEN T1.hostid > T2.hostid THEN T2.hostid
                           ELSE T1.hostid
                       END AS host2,
                       T1.userid AS userid,
                       CASE
                           WHEN T1.hostid > T2.hostid THEN T1.frequency
                           ELSE T2.frequency
                       END AS freq1,
                       CASE
                           WHEN T1.hostid > T2.hostid THEN T2.frequency
                           ELSE T1.frequency
                       END AS freq2,
					   T1.postmonth
      FROM
        ( SELECT TE1.userid AS userid,TE1.hostid AS hostid,TE1.postmonth AS postmonth, count(*) as frequency FROM
          (
              SELECT a.user_id AS userid,
                     b.host_user_id AS hostid,
             EXTRACT(month from b.post_date) as postmonth
             FROM `datacafethailand.social_insight.activity_feed` AS a
             INNER JOIN `datacafethailand.social_insight.host_x_txn` AS b ON a.key_id = b.key_id
             AND a.source=b.source
             UNION ALL SELECT a.user_id AS userid,
                              b.host_user_id AS hostid,
                  EXTRACT(month from b.post_date) as postmonth
             FROM `datacafethailand.social_insight.raw_feed` AS a
             INNER JOIN `datacafethailand.social_insight.host_x_txn` AS b ON a.key_id = b.key_id
             AND a.source=b.source
           ) AS TE1 GROUP BY TE1.userid,TE1.hostid,TE1.postmonth
         ) AS T1 /* user comment+like page A*/
      INNER JOIN
        ( 
          SELECT TE2.userid AS userid,TE2.hostid AS hostid,TE2.postmonth AS postmonth, count(*) as frequency FROM
          (
            SELECT a.user_id AS userid,
                   b.host_user_id AS hostid,
           EXTRACT(month from b.post_date) as postmonth
           FROM `datacafethailand.social_insight.activity_feed` AS a
           INNER JOIN `datacafethailand.social_insight.host_x_txn` AS b ON a.key_id = b.key_id
           AND a.source=b.source
           UNION ALL SELECT a.user_id AS userid,
                            b.host_user_id AS hostid,
                EXTRACT(month from b.post_date) as postmonth
           FROM `datacafethailand.social_insight.raw_feed` AS a
           INNER JOIN `datacafethailand.social_insight.host_x_txn` AS b ON a.key_id = b.key_id
           AND a.source=b.source
          ) AS TE2 GROUP BY TE2.userid,TE2.hostid,TE2.postmonth
        ) AS T2 ON T1.userid=T2.userid and T1.postmonth = T2.postmonth) T3
   GROUP BY 1,2,T3.postmonth) T4