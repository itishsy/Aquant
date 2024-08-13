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


def add_sub_task(parent_key, task_summary, task_description, task_assignee, task_component_id, task_priority=None, customfieldKeys=None, customfieldValues=None):
    issue_dict = {
        'project': {'key': 'SEEBOT'},
        'parent': {'key': parent_key},  # 指定父故事的问题键
        'summary': task_summary,
        'description': task_description,
        'issuetype': {'name': '子任务'},
        "assignee": {"name": task_assignee},  # 指定经办人用户名
        "components": [{"id": task_component_id}]  # 指定目标模块ID
    }

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
        print("子任务成功创建。")


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


if __name__ == '__main__':

    version = 'BOT20230707'

    # up_all_epic()
    all_story = find_all_story()
    for story in all_story:
        story_key = story.key
        summary = story.get_field('summary')
        if summary.endswith('社保') or summary.endswith('公积金'):
            if summary == '广州公积金':
                story.update(fields={'resolution': {"name": "未解决"}})
            # task_summary = "【" + summary + "】费用明细流程, 确认该地区的客户正确跑出数据"
            # task_description = "正确跑出该地区所有客户账户的费用数据，并在 参保管理 > 在户人数管理 > 费用明细, 可正确查询。"
            # task_component_id = '11015'  # 城市配置
            # # task_assignee = story.get_field('assignee').name
            # task_assignee = story.get_field('customfield_11102')
            # if task_assignee:
            #     # print(story_key, story.get_field('summary'), story.permalink())
            #     add_link_Test(story_key, task_summary, task_description, task_assignee.name, task_component_id)


    # find_story_no_task(version)
    # find_story_no_test(version, is_open=False)

    # update_task_version_by_story(version)

    # up_all_story_status(r_version)
