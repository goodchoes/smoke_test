import sys
sys.path.append("..")
from src import *
import argparse


if __name__=="__main__":
    g_config.parse_param()
    try:
        g_config.init_cfg()
    except Exception as e:
        logger.get(logger.RUN_LOG).exception(e)

    g_config.set("generator_test",True)
    g_config.set("tc_syntax_validation",True)

    logger.create_logging(logger.LOG_FOLDER,'validation_result','validation_result',False)
    log = logger.get('validation_result')
    uart = TerminalFactory.get_uart_terminal_simulator(log,'127.0.0.1','1234')
    bmc = TerminalFactory.get_ssh_terminal_simulator(log,g_config.get('bmc_ssh_addr'),g_config.get('bmc_ssh_user'),g_config.get('bmc_ssh_pass'))
    terminal_repo = TerminalRepo(uart,bmc)
    for module in g_config.TestModule:
        log.info('[Generator] @@@module:{} start analyse'.format(module))
        result = Parser(log,terminal_repo).run(g_config.get("test_case_file_path")[module])
        while (0 != len(result)):
            test_case = result.pop(0)
            log.info('[Generator] |--- start to run test case:{}'.format(test_case['name']))
            cmds = test_case[ProcedureType.CMD]
            expects = test_case[ProcedureType.EXPECT]
            teardown = test_case[ProcedureType.TEARDOWN]
            for (cmd, check) in zip(cmds, expects):
                cmd.do()
                check.do()
            for cmd in teardown:
                cmd.do()
        log.info('[Generator] @@@module:{} analyse over,no ERROR means pass'.format(module))
        log.info('')
