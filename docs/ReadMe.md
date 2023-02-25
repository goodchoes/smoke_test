# 测试工程使用说明

## 运行环境

   1. 需要在windows环境运行
   2. 需要python 3.10以上版本
   3. 需要需要安装一些python库，路径ftp://cpu_ver@@@10.233.166.14/smoke/resource password:Zhufeng1.0，下载到本地，将压缩包解压，执行下面命令

            安装python-3.10.5-amd64.exe,将python.exe文件所在路径，加入到系统环境变量中
            安装pip,将pip加入环境变量:
            进入pip-22.1.2目录>python setup.py install

            安装库文件
            cd pyserial-3.5> python setup.py install
            cd ftputil-5.0.4> python setup.py install
            pip install six-1.16.0-py2.py3-none-any.whl
            pip install bcrypt-4.0.1-cp36-abi3-win_amd64.whl
            pip install pycparser-2.21-py2.py3-none-any.whl
            pip install cffi-1.15.1-cp310-cp310-win_amd64.whl
            pip install cryptography-38.0.4-cp36-abi3-win_amd64.whl
            pip install PyNaCl-1.5.0-cp36-abi3-win_amd64.whl
            pip install paramiko-2.11.0-py2.py3-none-any.whl
            pip install lml-0.1.0-py2.py3-none-any.whl
            pip install pyexcel_io-0.6.6-py2.py3-none-any.whl
            pip install et_xmlfile-1.1.0-py3-none-any.whl
            pip install openpyxl-3.0.10-py2.py3-none-any.whl
            pip install pyexcel_xlsx-0.6.0-py2.py3-none-any.whl
            pip install scp-0.14.4-py2.py3-none-any.whl



## 运行测试工程
      
1. 下载代码

            仓库名称
            Zhufeng/cpu2.0/smoke-test

            https://gerrit.zte.com.cn/#/admin/projects/Zhufeng/cpu2.0/smoke-test

2. 部署工程
      将从git下载的smoke-test文件夹，放到Windows D盘目录下
      在src/main下执行
      python daily_smoke.py -print_level DEBUG -chip_topo [one_die,two_die,four_die]
      参数说明：
      print_level   用于控制冒烟运行过程中的日志信息等级，DEBUG是比较详细的等级，INFO信息较少
      chip_topo    用于指定冒烟的目标环境是哪种拓扑


3. 修改串口映射关系
      在.\utile\ChipTopo\OneDie.py文件下，修改串口映射关系代码,如果某个串口没有连接_uart_server_ports中可以不定义，然后将_uart_client_ports中其他已有串口，配置给未连接串口模块的客户端

        self._uart_server_ports={'N2':('COM5','1234'),\
            'SCP_DIE_0':('COM6','1235'),\
            'MCP_DIE_0':('COM4','1236')}
        self._uart_client_ports={'ATF':('COM5','1234'),\
            'UEFI':('COM5','1234'),\
            'N2':('COM5','1234'),\
            'SCP_DIE_0':('COM6','1235'),\
            'MCP_DIE_0':('COM4','1236')}
4. 如果用于压力测试，可以跳过版本下载和激活动作
      在.\utile\TestConfig.py文件中，修改DEBUG_SKIP_DOWNLOAD_FTP_PACKAGE和DEBUG_SKIP_ACTIVE_PACKAGE为True

## 修改用例

1. 请在test_cases目录下找到本模块的用例文件，进行修改
2. 修改完成后，需要运行script目录下的test_case_syntax_validation.py脚本，验证新增用例是否符合语法要求
   1. python test_case_syntax_validation.py -print_level [INFO | DEBUG] -chip_topo [one_die | two_die | four_die]
            参数说明：
            -print-level:指定脚本打印信息的等级，INFO只打印必须要的基本信息，DEBUG可以用于显示用例文件解析过程

            出现如下信息TEST FAIL，表示用例语法存在错误,需要根据提示修改
            2022-11-18 15:10:07,756 - Parser.py[line:136] - ERROR - [Generator] Case:3 name:shutdown_then_power_on, analyse Failed
            2022-11-18 15:10:07,757 - Parser.py[line:137] - ERROR - [Generator] =======!!!!!  FAIL INFO========:condition start flag [ must start first in cmd
            2022-11-18 15:10:07,757 - Parser.py[line:139] - ERROR - =======TEST FAIL=======
            -chip_topo：指定要测试环境的类型
      2. 错误码文件：.\src\generator\pub.py
          错误语法例子：.\src\generator\test\generator_test_cases.csv
3. 期望检测支持正则表达式
    如果用例参数，涉及到具体的硬件环境参数，那么需要执行如下流程：
   1. 将期望值作为，加入到test_cases目录下得具体环境文件中,例如one_die_config.csv用于验证单die环境，里面__CPU_NUM__用于描述，此测试环境的CPU个数，假设__CPU_NUM__期望值为64
   2. 然后__CPU_NUM__就可以在各个模块的用例csv文件中使用了，例如在Expect流程中加入：
      __RE::CPU\(s\):\s__CPU_NUM__,
      其中__RE::表示此次检查的目标字符串使用正则表达式，上面的信息是期望在lscpu命令的打印中，找到
      CPU(s):              53的打印，所对应的正则表达式
      如果没有__RE::开头，那么都会认为整个字符串，就是直接期望的输出值

## 用例文件格式介绍

1. 每个模块一个csv文件，每个文件中分为4列，我们把这些除了Name外的列，称作'流程'，每个流程可以包括下面要讲到的命令

   Name:
         用例名称
   Command:
         用例执行的命令，命令间用分号分割,例如uname -a;uname -a,执行前,不需要输入操作系统的登录用户名和密码
   Expect:
         与Command中命令对应的每个命令的期望的串口或BMC上的打印结果,用分号分割,
         元素个数需要与Command内命令个数一致,如果不需要检查可以只写分号
         期望的内容可以直接写期望的字符串，或者加上约束前缀，如[uart@@@xxx]Linux

   TearDown:
         清理用例执行后的垃圾,以便下一个用例执行


## 普通命令
1. 普通命令，例如在串口中执行reboot，表示在该命令在串口执行，并且不需要等待特定的时长或在特定终端下输入命令，
      如果想要指定在reboot之后，再等待一个特定时间长度，再执行其他命令，那么就要用到下面的约束前缀
2. 普通命令可以可以用于Command列，和TeartDown列

## 约束前缀命令
1. 约束前缀，包含 [ 或 ] 或 @@@ 或 ###字符的语句命令，都被认为，是有约束前缀的语句
2. 用于在检查测试结果，如[bmc@@@]Linux，表示在bmc下检查Linux的打印,也可以单独作为一个命令执行,如[uart@@@cmd:reboot],在串口下执行reboot指令
3. 约束前缀的模式包括[uart@@@xxx]或者[bmc@@@xxx]或者[uart@@@]或[bmc@@@]
4. ###符号用于在约束中，将各个指令隔开例如：[uart@@@cmd:uname -a;uname -a###wait:2;2],在UART串口中执行2次uname -a命令，然后插入###符号，指定后面开始是另一个指令,wait指令，该指令的元素个数需要与cmd命令中元素个数一致，每个元素之间使用分号分割，这里有2个元素，表示每个power status需要等待2秒，再执行下一个命令uname -a
5. 约束前缀命令，可以用于Command列，Expect列，TearDown列

## 指令
1. 只能在约束前缀中使用的语法,包括
   1. cmd,如[uart@@@cmd:reboot]
   2. time_out,如[uart@@@time_out:30]Linux
   3. wait,如[uart@@@wait:30]

## 宏
1. 宏被用于简化用例编写和屏蔽不同机型的不同参数，不同命令,可以在各个机型的配置文件中定义，例如：在testcase目录下的one_die_config.csv文件，two_die_config.csv文件，four_die_config.csv文件中定义，__SYS_RESTART__，用于约定系统reboot开始到结束的时间长度
   

## Word List
1. [uart@@@xxx]        

         约束前缀
         在uart上执行xxx定义的命令或等待xxx时长,uart@@@符号前面表示动作执行的环境是串口，后面是要执行的指令

2. [bmc@@@xxx]         

         约束前缀，在bmc的ssh会话命令行中执行xxx

3. cmd               

         只能在约束前缀内使用的指令，表示需要在串口或bmc的SSH会话中执行一个命令，多个命令间使用分号分割，
         cmd:x;y;z,表示x,y,z三条命令，命令间用分号分割

4. time_out          
         
         只能在约束前缀内使用的指令，范围[0,1800]
         表示等待串口或BMC会话打印，检查期望打印的最长时间，超过后，如果没有该打印，则认为失败，
         time_out:x, x表示某个命令期待的打印显示的超时时间
         带有time_out的约束前缀，只能在Expect流程中使用
         每个约束前缀中，只能有一个time_out时间，用于描述整个约束前缀等待超时时间，超时后，认为Expect流程失败
         单位是秒或者可以用___SYS_RESTART__来指定等待一个固定时长

5.  wait             
         
         只能在约束前缀内使用的指令，范围[0,1800],表示需要等待一段时间，再进行下一个约束前缀中的cmd指令的操作
         单位是秒或者可以用___SYS_RESTART__来指定等待一个固定时长，
         wait:x;x;x   x表示某个命令等待的时间间隔，需要与cmd元素个数一致

6.  __SYS_RESTART__  
         
         表示需要等待系统完成上电的一段时间长度，不同机型，可以在自己的配置文件中定义不同的值

7. __BMC_CMD__
         
         由于BMC命令有固定格式，而且比较长，所以使用此宏作为前缀，例如
        __BMC_CMD__ power on，中间需要有空格 
         等价于：
         ipmitool -H 192.254.1.2 -U admin -P superuser -I lanplus power on
         如果[bmc@@@xxx]中的命令没有添加__BMC_CMD__前缀，那么认为该字符串可以直接执行
         不同机型，可以在自己的配置文件中定义不同的值

8. __POWER_OFF__

         通过uart或bmc发送shutdown或power off需要等待的时间
         不同机型，可以在自己的配置文件中定义不同的值

            其他宏，可以自行定义到one_die_config.csv  two_die_config.csv four_die_config.csv文件中

## 复杂命令举例
         
1. 举例1：

            [bmc@@@cmd:power status###time_out:2]Chassis Power is off 
            在Expect流程中执行检查Chassis Power is off前，需要先执行前缀指定的动作，在BMC下执行命令power status,该命令期望2秒内得到打印输出

2. 举例2：

            uname -a;[bmc@@@cmd:power status;power status];uname -a;[bmc@@@cmd:power status;power status###wait:2;2###time_out:10]

            1. 第一条命令在串口执行uname -a命令，第一个命令结束后，用分号分割
            2. 第二条命令[bmc@@@cmd:power status;power status]，在BMC SSH会话中执行，cmd后面跟了2条power status命令，中间用分号分割
            3. 第三条命令，再次回到串口再次执行uname -a命令
            4 第四条命令,[bmc@@@cmd:power status;power status###wait:2;2###time_out:10]Linux,在BMC SSH会话中执行2次power status命令，然后插入###符号，指定后面开始是另一个指令,wait指令，该指令的元素个数需要与cmd命令中元素个数一致，每个元素之间使用分号分割，这里有2个元素，表示每个power status需要等待2秒，再执行下一个命令,整个条件在time_out:10秒内，要在BMC会话中检测到约束条件后的L打印，就算成功，如果超时，没有检测到，就失败

3. 举例3：

            [uart@@@cmd:uname -a],指定在串口种执行uname -a命令(当然使用默认的普通指令uname -a更方便)

## Example

        Name-----Command-------Expect----------TearDown
        power_on,   uname -a;uname -a,  Linux;Linux,

        reboot,        reboot,                       [uart@@@time_out:__SYS_RESTART__]localhost login,

        shutdown,   shutdown,                  [bmc@@@cmd:power status###time_out:2]Chassis Power is off,        [bmc@@@cmd:power on###wait:__SYS_RESTART__]

        bmc_check_power_on,                  [bmc@@@cmd:power status],         [bmc@@@]Chassis Power is on,

        power_on_useless,                         uname -a;uname -a,                  ;,

        shutdown_then_power_on,           [uart@@@cmd:shutdown###wait:10];[bmc@@@cmd:power on],   [bmc@@@cmd:power status]Chassis Power is off;[uart@@@time_out:__SYS_RESTART__]CGS Linux,    

        check_numa_node_num,               lscpu,                         __RE::NUMA node\(s\):\s__NUMA_NODE_NUM__, 


1. power_on用例：
         在串口上执行两次uname -a命令:uname -a;uname -a,最终期望在串口中"Linux"字符串，会在每次执行命令后都出现在串口打印中
2. reboot用例:
         在串口中执行reboot命令，由于复位需要很长时间，需要用time_out指令说明，
         如果超过___SYS_RESTART__对应的时间，例如300秒，在串口没有检测到期望localhost login的打印，则失败
3. shutdown用例：
         在串口中执行shutdown命令，然后期望在BMC会话中通过执行power status命令，在2秒内，得到Chassis Power is off打印
         由于shutdown用例会导致系统掉电，因此，需要在TearDown中恢复系统状态，通过[bmc@@@cmd:power on###wait:__SYS_RESTART__]，让BMC给系统上电
4. bmc_check_power_on用例:
         在BMC的SSH会话中执行了[bmc@@@cmd:power status]命令，期望在BMC会话中得到包含Chassis Power is on的打印
5. power_on_useless
         该用例支持，但是没有意义，因为无法校验用例成功或失败
6. shutdown_then_power_on用例：
         支持命令从uart输入，在bmc中检查结果，反过来，也支持
7. check_numa_node_num用例：
          在串口中OS下输入lscpu命令，打印的格式不确定，因此使用正则，例如期望打印是，NUMA node(s):        1


## 其他说明

1. 每行用例解析的过程中，如果发生解析失败，会记录错误，并忽略本条用例，在冒烟结果中，会按将解析失败信息，记录到该模块的log日志中
2. 现在的版本，由于mcp和scp,uefi，不支持cli配置接口，因此，还不能新增用例，现在只能在n2_test_case.csv文件中，增加在进入OS后的用例