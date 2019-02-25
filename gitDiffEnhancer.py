    global ctx, curr_branch, unStash
    unStash = False
    # 未指定 --pname 工作区 默认为当前文件夹
    if not workPath:
        if valider_path(os.path.join(os.getcwd(), '.git')) == _DIR:
            workPath = os.getcwd()
        else:
            raise RuntimeError('未指定--pname参数且当前文件夹非git项目')
    if os.system('git --version') != 0:
        raise RuntimeError('git配置有误,检查git配置')
    else:
        if os.system('git show %s %s --name-only' % (oldCommitId, newCommitId)) != 0:
            raise RuntimeError('不正确的commitId参数,检查--ocid和--ncid参数')
        # 保存现场
        for line in os.popen('git branch').readlines():
            if line.startswith('*'):
                curr_branch = line[1:].strip()
                break
        os.system('git stash save "temp_statsh_for_update"')
        os.system('git checkout %s' % newCommitId)
        basePath = workPath.rstrip(os.sep)
        ctx = basePath[basePath.rfind(os.sep) + 1:]
        compile_workspace()
        os.system('git diff %s %s > diff.patch' % (oldCommitId, newCommitId))
        # 创建补丁包文件夹
        try:
            os.mkdir(ctx)
        except FileExistsError:
            shutil.rmtree(ctx)
            os.mkdir(ctx)

        # 遍历diff action
        with open('diff.patch', errors='ignore') as fr:
            while line:
                matcher = re.match(r'^diff --git a/(.*) b/(.*)', line)
                if matcher is not None:
                    a = matcher.group(1)
                    if a.endswith(COMPLEX_HANDLE_FILE_TYPE):  # 复杂处理类型
                        fr.seek(handle_complex_file_type(a, fr.tell()))
                    else:
                        try:
                            if a.startswith('src/main/resources'):
                                handle_src_main_resources(a)
                            elif a.startswith('src/main/webapp'):
                                handle_src_main_webapp(a)
                            elif a.startswith('src/main/java'):
                                handle_src_main_java(a)
                        except FileNotFoundError:
                            OUT_PUT_LIST['delete'].append(a)
                line = fr.readline()
    except:
        # 异常恢复现场
        unStash = True
        os.system('git checkout %s' % curr_branch)
        os.system('git stash pop')
        raise RuntimeError('编译工作区发生异常')
    # 正常恢复现场
    if not unStash:
        os.system('git checkout %s' % curr_branch)
        os.system('git stash pop')
    编译工作区 jdk8+maven3.x,
    针对eclipse项目和idea项目做不同路径查询处理
        if not valider_path('pom.xml') == _FILE:
    # 找寻输出路径
    global CLASSPATH
            for child in ET.parse('.classpath').getroot():
                if child.tag == 'classpathentry' and child.attrib['kind'] == 'output':
                    CLASSPATH = os.path.join(os.getcwd(), child.attrib['path'])
                for child in ET.parse('%s.iml' % ctx).getroot():
                    if child.tag == 'component' and child.attrib['name'] == 'NewModuleRootManager':
                        output = child.find('output').attrib['url']
                        CLASSPATH = os.path.join(os.getcwd(),
                                                 output[output.find('/$MODULE_DIR$/') + len('/$MODULE_DIR$/'):])
            raise RuntimeError('非eclipse或IDEA项目 未找到.classpath文件或iml文件')
    if os.system('mvn clean compile -Dfile.encoding=UTF-8 -Dmaven.test.skip=true') != 0:
        raise RuntimeError('项目编译失败 检查配置')
    # 只填写了一个commit参数 默认为HEAD
    if args.ocid and not args.ncid:
        args.ncid = 'HEAD'

    if not args.ocid and args.ncid:
        args.ocid = args.ncid
        args.ncid = 'HEAD'

    if not args.ocid or not args.ncid:
        raise RuntimeError('参数指定不完整:--ocid(旧提交) --ncid(新提交) short hash index')

    start = time.process_time()

    try:
        starter(args.pname, args.ocid, args.ncid)
        cleaner(args.ocid, args.ncid)
    except:
        pass
    print('operation is success exit. used time : %ss' % (time.process_time() - start))