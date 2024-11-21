from jira import JIRA

jira_server = 'http://192.168.0.87:8080/'
jira_username = 'huangshouyi'
jira_password = '123456'

jira = JIRA(basic_auth=(jira_username, jira_password), options={'server': jira_server})


# 刷新史诗自定义字段
def up_epic(epic_key):
    epic = jira.issue(id=epic_key)
    epic_story = jira.search_issues('project = RPA AND issuetype = 故事 AND 史诗链接 = {}'.format(epic_key), maxResults=1000)
    sb_story, gjj_story, sj_story = 0, 0, 0
    for story_key in epic_story:
        story = jira.issue(id=story_key)
        story_status = 0
        for link_id in story.fields.issuelinks:
            task = jira.issue_link(link_id).inwardIssue
            print(task.key, task.fields.issuetype, task.fields.summary, task.fields.status)
            if str(task.fields.issuetype) == "任务" and (
                    str(task.fields.status) == "已完成" or str(task.fields.status) == "已关闭"):
                story_status = 1

        for link_id in story.fields.issuelinks:
            task = jira.issue_link(link_id).inwardIssue
            if str(task.fields.issuetype) == "Test" and (
                    str(task.fields.status) == "已完成" or str(task.fields.status) == "完成" or str(
                task.fields.status) == "已关闭"):
                story_status = 2
                story.fields.status = '已完成'

        story_summary = story.fields.summary
        epic_status_value = "配置中"
        if story_status == 0:
            epic_status_value = "配置中"
        elif story_status == 1:
            epic_status_value = "盒子测试中"
        elif story_status == 2:
            epic_status_value = "√"

        # {'id': 'customfield_10603', 'name': '社保'}
        # {'id': 'customfield_10604', 'name': '公积金'}
        # {'id': 'customfield_10605', 'name': '实缴'}
        if "社保" in story_summary:
            sb_story = 1
            epic.update(fields={'customfield_10603': {'value': epic_status_value}})
        if "公积金" in story_summary:
            gjj_story = 1
            epic.update(fields={'customfield_10604': {'value': epic_status_value}})
        if "实缴" in story_summary:
            sj_story = 1
            epic.update(fields={'customfield_10605': {'value': epic_status_value}})
            # print(story_summary, "社保配置中")
    if sb_story == 0:
        epic.update(fields={'customfield_10603': {'value': '--'}})
    if gjj_story == 0:
        epic.update(fields={'customfield_10604': {'value': '--'}})
    if sj_story == 0:
        epic.update(fields={'customfield_10605': {'value': '--'}})


# 刷新任务的修复版本
def update_task_version_by_story(version):
    story_arr = jira.search_issues('project = "RPA" AND issuetype="故事" AND fixVersion="{}"'.format(version),
                                   maxResults=1000)
    for story_key in story_arr:
        story = jira.issue(id=story_key)
        for link_id in story.fields.issuelinks:
            link_issue = jira.issue_link(link_id).inwardIssue
            issue = jira.issue(id=link_issue.key)
            need_update = True
            fixVersions = []
            for issue_version in issue.fields.fixVersions:
                fixVersions.append({'name': issue_version.name})
                if issue_version.name == version:
                    need_update = False
            if need_update:
                print("append issue fixVersions：", version)
                fixVersions.append({'name': version})
                issue.update(fields={'fixVersions': fixVersions})

            if str(issue.fields.issuetype) == "Test":
                for link_id2 in issue.fields.issuelinks:
                    link_issue2 = jira.issue_link(link_id2).inwardIssue
                    issue2 = jira.issue(id=link_issue2.key)
                    if str(issue2.fields.issuetype) == "故障" and ('SEEBOT' in issue2.key):
                        need_update2 = True
                        fixVersions2 = []
                        for issue_version2 in issue2.fields.fixVersions:
                            fixVersions2.append({'name': issue_version2.name})
                            if issue_version2.name == version:
                                need_update2 = False
                        if need_update2:
                            print("append issue fixVersions：", version)
                            fixVersions2.append({'name': version})
                            issue2.update(fields={'fixVersions': fixVersions2})


# 刷新故事的状态
def up_story_status(story_key):
    story = jira.issue(id=story_key)
    up_flag = False
    for link_id in story.fields.issuelinks:
        task = jira.issue_link(link_id).inwardIssue
        print(task.key, task.fields.issuetype, task.fields.summary, task.fields.status)
        if str(task.fields.issuetype) == "任务":
            if str(task.fields.status) == "已完成" or str(task.fields.status) == "已关闭":
                up_flag = True
            else:
                break

    if up_flag:
        for link_id2 in story.fields.issuelinks:
            test = jira.issue_link(link_id2).inwardIssue
            print(test.key, test.fields.issuetype, test.fields.summary, test.fields.status)
            if str(test.fields.issuetype) == "Test" and (
                    str(test.fields.status) == "已完成" or str(test.fields.status) == "完成" or str(
                test.fields.status) == "已关闭"):
                if "'21'" in str(jira.transitions(story)):
                    jira.transition_issue(story, transition='21')
                # story.update(status={'name': '已完成'})
                print(story.key, story.fields.issuetype, story.fields.summary, story.fields.status)


def up_all_epic():
    epic_arr = jira.search_issues('project = "SEEBOT" AND issuetype="Epic"', maxResults=1000)
    for epic_key in epic_arr:
        # print(epic_key)
        epic = jira.issue(id=epic_key)
        if epic.fields.summary.find('盒子') > 0:
            up_epic(epic_key)
        # epic.update(fields={'components': [{'name': "盒子上线地区", "id": "10552"}]})

def update_story_status(story, status):
    transitions = jira.transitions(story)
    for tran in transitions:
        if tran['name'] == status:
            tran_id = tran['id']
            jira.transition_issue(story, transition=tran_id)
            print("故事[", story.get_field('summary'), "],状态更新为:", status)

def up_all_story_status(version):
    story_arr = jira.search_issues('project = "SEEBOT" AND issuetype="故事" AND fixVersion="{}"'.format(version),
                                   maxResults=1000)
    for story_key in story_arr:
        up_story_status(story_key)


def add_sub_task(parent_key, task_summary, task_description, task_assignee, task_component_id, fixVersions=None, task_priority=None, customfieldKeys=None, customfieldValues=None):
    issue_dict = {
        'project': {'key': 'SEEBOT'},
        'parent': {'key': parent_key},  # 指定父故事的问题键
        'summary': task_summary,
        'description': task_description,
        'issuetype': {'name': '子任务'},
        "assignee": {"name": task_assignee},  # 指定经办人用户名
        "components": [{"id": task_component_id}]  # 指定目标模块ID
    }
    if fixVersions:
        issue_dict['fixVersions'] = [{"name": fixVersions}]  # 指定修复的版本

    if task_priority:
        issue_dict['priority'] = {"name": task_priority}  # 指定优先级

    if customfieldKeys and customfieldValues:
        if len(customfieldKeys) == len(customfieldValues):
            i = 0
            for key in customfieldKeys:
                issue_dict[key] = customfieldValues[i]
                i = i+1
        else:
            print("自定义字段键值参数错误")
            return

    new_issue = jira.create_issue(fields=issue_dict)
    if new_issue:
        print("子任务成功创建。", task_summary, new_issue.permalink())


def add_link_Test(story_key, task_summary, task_description, task_assignee, task_component_id, customfieldKeys=None, customfieldValues=None):
    issue_dict = {
        'project': {'key': 'SEEBOT'},
        'summary': task_summary,
        'description': task_description,
        'issuetype': {'name': 'Test'},
        "assignee": {"name": task_assignee},  # 指定经办人用户名
        "components": [{"id": task_component_id}]  # 指定模块
    }

    if customfieldKeys and customfieldValues:
        if len(customfieldKeys) == len(customfieldValues):
            i = 0
            for key in customfieldKeys:
                issue_dict[key] = customfieldValues[i]
                i = i+1
        else:
            print("自定义字段键值参数错误")
            return

    new_issue = jira.create_issue(fields=issue_dict)
    if new_issue:
        jira.create_issue_link('Tests', new_issue.key, story_key)
        print("故事的测试任务创建成功。")


def find_story_no_test(version, is_open=True):
    print('当前版本【{}】故事，未开始测试（无测试任务或测试任务为待办）'.format(version))
    story_arr = jira.search_issues(
        'project = "SEEBOT" AND issuetype="故事" AND status="In Progress" AND fixVersion="{}"'.format(version),
        maxResults=1000)
    for story_key in story_arr:
        story = jira.issue(id=story_key)
        test_flag = True
        for link_id in story.fields.issuelinks:
            task = jira.issue_link(link_id).inwardIssue
            if str(task.fields.issuetype) == "Test":
                test_flag = False
                if is_open:
                    if str(task.fields.status) == "Open" or str(task.fields.status) == "待办":
                        test_flag = True
                    else:
                        break
        if test_flag:
            print(story.permalink())


def find_all_story(version=None):
    print('版本【{}】故事，未挂开发任务,或开发任务不在当前版本'.format(version))
    if version == None:
        story_arr = jira.search_issues('project = "SEEBOT" AND issuetype="故事"', maxResults=1000)
    else:
        story_arr = jira.search_issues('project = "SEEBOT" AND issuetype="故事" AND fixVersion="{}"'.format(version),
                                   maxResults=1000)
    res = []
    for story_key in story_arr:
        sto = jira.issue(id=story_key)
        res.append(sto)
        # print(sto.get_field('summary'), sto.permalink())
    return res

def update_story_task_summary(story, ori_summary, new_summary):
    subtasks = story.fields.subtasks
    for subtask in subtasks:
        if subtask.get_field('summary').endswith(ori_summary):
            subtask.update(summary=new_summary)


def find_story_no_task(version):
    print('版本【{}】故事，未挂开发任务,或开发任务不在当前版本'.format(version))
    story_arr = jira.search_issues('project = "SEEBOT" AND issuetype="故事" AND fixVersion="{}"'.format(version),
                                   maxResults=1000)
    for story_key in story_arr:
        story = jira.issue(id=story_key)
        t_flag = True
        for link_id in story.fields.issuelinks:
            task = jira.issue_link(link_id).inwardIssue
            if str(task.fields.issuetype) == "任务":
                t_flag = False
                break

        if t_flag and len(story.fields.subtasks) == 0:
            print(story.permalink())


def find_issues(project='SEEBOT', version=""):
    issue_arr = jira.search_issues('project = "SEEBOT" AND fixVersion="{}"'.format(version), maxResults=1000)
    issues = []
    for issue_key in issue_arr:
        issue = jira.issue(id=issue_key, expand='changelog')
        issues.append(issue)
    return issues


def find_un_close_story(version=""):
    print('版本【{}】开发及测试任务已完成，故事未关闭'.format(version))
    story_arr = jira.search_issues(
        'project = "SEEBOT" AND issuetype="故事" AND fixVersion="{}" AND status in (Open,"In Progress", 已完成)'.format(
            version),
        maxResults=1000)

    for story_key in story_arr:
        story = jira.issue(id=story_key)
        story_status = 0
        for link_id in story.fields.issuelinks:
            task = jira.issue_link(link_id).inwardIssue
            if str(task.fields.issuetype) == "任务":
                if (str(task.fields.status) == "已完成" or str(task.fields.status) == "已关闭"):
                    story_status = 1
                else:
                    story_status = 0
                    break

        if story_status == 1:
            for link_id in story.fields.issuelinks:
                task = jira.issue_link(link_id).inwardIssue
                if str(task.fields.issuetype) == "Test":
                    if (str(task.fields.status) == "已完成" or str(task.fields.status) == "完成" or str(
                            task.fields.status) == "已关闭"):
                        story_status = 2
                    else:
                        story_status = 1
                        break
        if story_status == 2:
            print(story.permalink())

# 复盘统计
def version_tj(version, start_time, end_time):
    users = {'chaodongyue': "巢东岳",
             'chenjingchun': "陈静纯",
             'fengweilong': '冯尾龙',
             'huangshouyi': '黄首益',
             'liangheyun': '梁鹤云',
             'lirongwei': '李荣威',
             'lisongyang': '李松洋',
             'liudandan': '刘丹丹',
             'liuhongchang': '刘洪昌',
             'liwensha': '李文莎',
             'lixiaolong': '李小龙',
             'pengshasha': '彭莎莎',
             'tanyong': '谭咏',
             'wangying': '王英',
             'weizhaoxin': '韦兆新',
             'xufuzhou': '徐富周',
             'yanglianxin': '杨廉新',
             'zengyixin': '曾轶鑫',
             'zhangkailun': '张凯伦',
             'zhengjiajie': '郑佳杰',
             'zhenshijun': '甄仕军'}

    usernames = users.keys()
    print("版本：", version)
    total = 0
    done_size = 0
    add_size = 0
    delay_size = 0
    InView_size = 0

    for user in usernames:
        # 版本统计
        issues = jira.search_issues('fixVersion in ({}) AND assignee in ({}) '.format(version, user), expand='changelog')

        done_arr = []
        add_arr = []
        delay_arr = []
        InView_arr = []
        task_arr = []
        bug_arr = []
        for issue in issues:
            if issue.fields.issuetype.name == '故障':
                bug_arr.append(issue)
            elif issue.fields.issuetype.name in ['任务', 'Test', '故事', '子任务']:
                task_arr.append(issue)

            if issue.get_field('created') > start_time:
                add_arr.append(issue)

            status = issue.get_field('status').name
            if status in ['待办', '处理中', '开放']:
                delay_arr.append(issue)
            elif status in ['完成', '已完成', '关闭']:
                done_arr.append(issue)

        if user in ['liwensha', 'lixiaolong', 'chenjingchun', 'yanglianxin']:
            bugs = jira.search_issues('fixVersion in ({}) AND reporter in ({}) '.format(version, user),
                                      maxResults=1000, expand='changelog')
            for bug in bugs:
                bug_arr.append(bug)

                if bug.get_field('created') > start_time and bug.get_field('created') < end_time:
                    add_arr.append(bug)

                if bug.get_field('status').name == 'In View':
                    InView_arr.append(bug)
                elif bug.get_field('status').name in ['完成', '已完成', '关闭']:
                    done_arr.append(bug)

        if len(issues) > 0:
            total = total + len(issues)
            done_size = done_size + len(done_arr)
            add_size = add_size + len(add_arr)
            delay_size = delay_size + len(delay_arr)
            InView_size = InView_size + len(InView_arr)

            print(users.get(user), "任务：", "{}+{}".format(len(task_arr), len(bug_arr)), "完成：", len(done_arr), "插入：",
                  len(add_arr), "延迟：", "{}+{}".format(len(delay_arr), len(InView_arr)))
            for delay in delay_arr:
                comment_txt = ''
                comments = delay.fields.comment.comments
                if len(comments) > 0:
                    for comment in comments:
                        if start_time < comment.created < end_time:
                            comment_txt = comment_txt + comment.body
                print(delay.permalink(), delay.get_field('summary'),
                      '插入' if delay.get_field('created') > start_time else '', comment_txt)
            for inView in InView_arr:
                comment_txt = ''
                comments = inView.fields.comment.comments
                if len(comments) > 0:
                    for comment in comments:
                        if start_time < comment.created < end_time:
                            comment_txt = comment_txt + comment.body
                print(inView.permalink(), inView.get_field('summary'),
                      '插入' if inView.get_field('created') > start_time else '', comment_txt)

    print("总数", total, "插入", add_size, "完成", done_size, "延迟", delay_size, "延迟验证", InView_size)


if __name__ == '__main__':
    version = 'BOT20241031,RPA20241031'
    version_tj(version=version, start_time='2024-10-19', end_time='2024-10-31')

'''
    # 创建子任务
    all_story = find_all_story()
    for story in all_story:
        story_summary = story.get_field('summary')
        if story_summary in ['柳州社保','合肥社保','深圳社保','太原社保','广州社保','惠州社保','晋中社保','天津社保','沈阳社保','大连社保','东莞社保','北京社保','长春社保','泉州社保','西安社保','海口社保','郑州社保','武汉社保','无锡社保','厦门社保']:
            task_assignee = story.get_field('assignee')     # 经办人
            if task_assignee:
                story_key = story.key
                task_summary = "【" + story_summary + "】优化税务端填报基数流程，需要确保提交名单必需与增员成功名单一致"
                task_description = """税务端填报基数流程，需要复核提交名单必需与增员成功名单一致
                参考长春-社保处理方式
                咨询佳杰
            """
                task_component_id = '11015'  # 城市配置
                add_sub_task(story_key, task_summary, task_description, task_assignee.name, task_component_id, fixVersions =version)


    # 更新维护人
    all_story = find_all_story()
    for story in all_story:
        summary = story.get_field('summary')
        if summary == '广州社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '珠海社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '佛山社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '江门社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '湛江社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '茂名社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '肇庆社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '惠州社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '汕尾社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '河源社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '阳江社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '清远社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '东莞社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '中山社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
        if summary == '揭阳社保':
            story.update(fields={'customfield_11102': {'name': 'yanglianxin'}})
'''


'''
    # 查询修改记录
    issues = jira.search_issues('project = "SEEBOT" AND fixVersion="{}"'.format(version), maxResults=1000, expand='changelog')
    for issue in issues:
        for history in issue.changelog.histories:
            for item in history.items:
                if item.field == 'Fix Version' and item.toString == 'BOT20240831':
                    print(f"issue: {issue.key} ", issue.get_field('summary') , issue.get_field('assignee'))
                    # print(f"\tField: {item.field}")
                    # print(f"\tFrom: {item.fromString}")
                    # print(f"\tTo: {item.toString}")
                    # print(f"\t")
'''

'''
    issues = jira.search_issues('project = "SEEBOT" AND issuetype="Test"', maxResults=1000)
    for issue in issues:
        summary = issue.get_field('summary')
        if '在册流程,' in summary:
            status = issue.get_field('status')
            if status.name == '已完成':
                print(summary.split('】')[0], status)
'''

'''
    # up_all_epic()
    all_story = find_all_story()
    for story in all_story:
        story_key = story.key
        summary = story.get_field('summary')
        if summary.endswith('社保') or summary.endswith('公积金'):
            # if summary.endswith('郑州社保'):
            task_summary = "【" + summary + "】信息配置，标准化命名登录方式"
            task_description = """要求：
            1. 每个网站系统必须要配置登录方式，且统一命名字段名称和字段key为：
            社保登录方式 socialLoginType
            养老登录方式 ylLoginType
            医疗登录方式 medicalLoginType
            工伤登录方式 gsLoginType
            单工伤登录方式 dgsLoginType
            备案登录方式 baLoginType
            税务登录方式 taxLoginType
            金保登录方式 jbLoginType
            失业登录方式 syLoginType
            市网登录方式 swLoginType
            公积金登录方式 accfundLoginType

            2. 没有配置登录方式，需要按标准命名配置登录方式。

            3. 有配置登录方式且与标准命名不一致，修改过程： （1) 加上新key。（2）所有的户（包括万科和仕邦所有客户）将旧key的值填写到新key上。（3）在信息配置中删除旧key（必须完成第（2）后）

            4. 检查登录流程，步骤中原来使用旧key的，配置成新key

            5. 登录方式下拉选项默认为五种：账号密码登录,CA证书登录,扫码登录,短信登录,接收器验证
            如果登录方式中再有细分，需要加上前缀。比如网站有提供电子营业执照和APP2种扫码方式。扫码登录就要加上前缀，细分为：电子营业执照扫码登录、APP扫码登录

            6. 登录方式下拉值更改后，需要确认所有户（包括万科和仕邦所有客户）的下拉选择正确。

            """
            subtasks = story.fields.subtasks
            for subtask in subtasks:
                if subtask.get_field('summary').endswith('【合肥社保】在册流程, 确认该地区的客户正确跑出数据'):
                    changelog = jira.changelog(subtask)
                    for history in changelog.histories:
                        for item in history.items:
                            print(f"\tField: {item.field}")
                            print(f"\tFrom: {item.fromString}")
                            print(f"\tTo: {item.toString}")
                            print(f"\t")

                #     subtask.update(description=task_description)


            # task_component_id = '11015'  # 城市配置
            # task_assignee = story.get_field('assignee')  # 经办人
            # task_assignee = story.get_field('customfield_11102') # 维护人
            # if task_assignee:
            #     add_sub_task(story_key, task_summary, task_description, task_assignee.name, task_component_id)
                # print(story_key, story.get_field('summary'), story.permalink())
                # add_link_Test(story_key, task_summary, task_description, task_assignee.name, task_component_id)
'''

    # find_story_no_task(version)
    # find_story_no_test(version, is_open=False)

    # update_task_version_by_story(version)

    # up_all_story_status(r_version)
