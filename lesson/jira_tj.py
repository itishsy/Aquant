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
def update_task_version_by_story(story_key, version):
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
                if str(issue2.fields.issuetype) == "故障" and ('RPA' in issue2.key):
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
    epic_arr = jira.search_issues('project = "RPA" AND issuetype="Epic"', maxResults=1000)
    for epic_key in epic_arr:
        epic = jira.issue(id=epic_key)
        # epic.update(fields={'components': [{'name': "盒子上线地区", "id": "10552"}]})
        up_epic(epic_key)


def up_all_story_version(version="RPA20230421"):
    story_arr = jira.search_issues('project = "RPA" AND issuetype="故事" AND fixVersion="{}"'.format(version),
                                   maxResults=1000)
    for story_key in story_arr:
        update_task_version_by_story(story_key, version)


def up_all_story_status():
    version = "RPA20230414"
    story_arr = jira.search_issues('project = "RPA" AND issuetype="故事" AND fixVersion="{}"'.format(version),
                                   maxResults=1000)
    for story_key in story_arr:
        up_story_status(story_key)


def find_story_no_test(version="SaaS20230421"):
    print('当前版本【{}】故事，未挂测试任务'.format(version))
    story_arr = jira.search_issues('project = "RPA" AND issuetype="故事" AND fixVersion="{}"'.format(version),
                                   maxResults=1000)
    for story_key in story_arr:
        story = jira.issue(id=story_key)
        test_flag = True
        for link_id in story.fields.issuelinks:
            task = jira.issue_link(link_id).inwardIssue
            if str(task.fields.issuetype) == "Test":
                test_flag = False
                break
        if test_flag:
            print(story.permalink())


def find_story_no_task(version="SaaS20230421"):
    print('版本【{}】故事，未挂开发任务,或开发任务不在当前版本'.format(version))
    story_arr = jira.search_issues('project = "RPA" AND issuetype="故事" AND fixVersion="{}"'.format(version),
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
        'project = "RPA" AND issuetype="故事" AND fixVersion="{}" AND status in (Open,"In Progress", 已完成)'.format(
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
    up_all_epic()

    # r_version = 'RPA20230421'
    # s_version = 'SaaS20230421'

    # find_story_no_task(r_version)
    # find_story_no_task(s_version)

    # find_story_no_test(r_version)
    # find_story_no_test(s_version)

    # up_all_story_version(r_version)
    # up_all_story_version(s_version)
    # find_story_no_test()
    # up_all_story_status()
    # up_story_status('RPA-1385')
    # up_all_story_version()
    # up_epic('RPA-1727')
    # up_version('RPA-938',version)
