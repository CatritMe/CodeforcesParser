
import requests

from utils import get_tags

contest = requests.get('https://codeforces.com/api/problemset.problems?}')
# список задач из архива
result = contest.json()['result']['problems']
# статистика решений задач
statistic = contest.json()['result']['problemStatistics']
# for res in result:
#     print(res)

for st in statistic:
    print(st)

# for i in range(len(statistic)):
#     if statistic[i]['contestId'] == 3 and statistic[i]['index'] == 'A':
#         print(statistic[i])
#
# tags = []
# for res in result:
#     for tag in res['tags']:
#         if tag not in tags:
#             tags.append(tag)
# print(tags)

"""
['dfs and similar'910, 'divide and conquer'280, 'graphs'1040, 'combinatorics'656, 'dp'2064, 
'math'2798, 'brute force'1624, 'data structures'1684, 
'greedy'2758, 'sortings'1048, 'two pointers'521, 'strings'711, 'implementation'2668, 
'interactive'219, '797', 'dsu'345, 'games'218, 'hashing'205, 
'number theory'719, 'binary search'1024, 'geometry'387, 'constructive algorithms'1696, 
'string suffix structures'90, 'bitmasks'553, 
'probabilities'231, 'meet-in-the-middle'49, 'matrices'118, 'ternary search'53, 'fft'91, 
'shortest paths'261, '2-sat'32, 'flows'143, 
'*special'427, 'graph matchings'89, 'schedules'10, 'expression parsing'36, 'chinese remainder theorem'16]
"""

"""
SELECT problems.contest_id, problems.index, problems.name, problems.rating, problems.solved_count, tags.tag_name
FROM problems 
JOIN problems_tags ON problems.contest_id = problems_tags.contest_id 
AND problems.index = problems_tags.index 
JOIN tags ON tags.tag_name = problems_tags.tag_name
where tags.tag_name = 'chinese remainder theorem'
order by problems.rating, tags.tag_name, problems.contest_id, problems.index;
select * from tags WHERE tags.tag_name = 'interactive';
"""
