import json
import logging, traceback, sys, threading
import schedule
import time
from config import conf
try:
    import Queue
except ImportError:
    import queue as Queue

from ..log import set_logging
from ..utils import test_connect
from ..storage import templates

logger = logging.getLogger('itchat')

group_id_zzy = ''

def load_register(core):
    core.auto_login       = auto_login
    core.configured_reply = configured_reply
    core.msg_register     = msg_register
    core.run              = run

def auto_login(self, hotReload=False, statusStorageDir='itchat.pkl',
        enableCmdQR=False, picDir=None, qrCallback=None,
        loginCallback=None, exitCallback=None):
    if not test_connect():
        logger.info("You can't get access to internet or wechat domain, so exit.")
        sys.exit()
    self.useHotReload = hotReload
    self.hotReloadDir = statusStorageDir
    if hotReload:
        rval=self.load_login_status(statusStorageDir,
                loginCallback=loginCallback, exitCallback=exitCallback)
        if rval:
            return
        logger.error('Hot reload failed, logging in normally, error={}'.format(rval))
        self.logout()
        self.login(enableCmdQR=enableCmdQR, picDir=picDir, qrCallback=qrCallback,
            loginCallback=loginCallback, exitCallback=exitCallback)
        self.dump_login_status(statusStorageDir)
    else:
        self.login(enableCmdQR=enableCmdQR, picDir=picDir, qrCallback=qrCallback,
            loginCallback=loginCallback, exitCallback=exitCallback)

def configured_reply(self):
    ''' determine the type of message and reply if its method is defined
        however, I use a strange way to determine whether a msg is from massive platform
        I haven't found a better solution here
        The main problem I'm worrying about is the mismatching of new friends added on phone
        If you have any good idea, pleeeease report an issue. I will be more than grateful.
    '''
    try:
        msg = self.msgList.get(timeout=1)
    except Queue.Empty:
        pass
    else:
        try:
            if isinstance(msg['User'], templates.User):
                replyFn = self.functionDict['FriendChat'].get(msg['Type'])
            elif isinstance(msg['User'], templates.MassivePlatform):
                replyFn = self.functionDict['MpChat'].get(msg['Type'])
            elif isinstance(msg['User'], templates.Chatroom):
                replyFn = self.functionDict['GroupChat'].get(msg['Type'])
            if replyFn is None:
                r = None
            else:
                r = replyFn(msg)
                if r is not None:
                    self.send(r, msg.get('FromUserName'))
        except:
            logger.warning(traceback.format_exc())

def msg_register(self, msgType, isFriendChat=False, isGroupChat=False, isMpChat=False):
    ''' a decorator constructor
        return a specific decorator based on information given '''
    if not (isinstance(msgType, list) or isinstance(msgType, tuple)):
        msgType = [msgType]
    def _msg_register(fn):
        for _msgType in msgType:
            if isFriendChat:
                self.functionDict['FriendChat'][_msgType] = fn
            if isGroupChat:
                self.functionDict['GroupChat'][_msgType] = fn
            if isMpChat:
                self.functionDict['MpChat'][_msgType] = fn
            if not any((isFriendChat, isGroupChat, isMpChat)):
                self.functionDict['FriendChat'][_msgType] = fn
        return fn
    return _msg_register

def run(self, debug=False, blockThread=True):
    logger.info('Start auto replying.')
    if debug:
        set_logging(loggingLevel=logging.DEBUG)
    def reply_fn():
        try:
            while self.alive:
                self.configured_reply()
        except KeyboardInterrupt:
            if self.useHotReload:
                self.dump_login_status()
            self.alive = False
            logger.debug('itchat received an ^C and exit.')
            logger.info('Bye~')
    
    def job_zzy_drink():
        self.send_msg('@Zzy 肉肉喝水啦 ~ [定时发送]', group_id_zzy)

    def job_zzy_flow_checking():
        self.send_msg('@Zzy 肉肉查流程啦 ~ [定时发送]', group_id_zzy)
    
    def reply_fn_timing_zzy():
        try:
            for moment in ["10:00", "13:00", "15:00", "17:00"]:
                schedule.every().day.at(moment).do(job_zzy_drink)
            for moment in ["11:00", "14:00", "18:00"]:
                schedule.every().day.at(moment).do(job_zzy_flow_checking)
            while self.alive:
                for chatroom in self.get_chatrooms():
                    if chatroom.get('NickName') == conf().get('group_timing_group_map').get('reply_fn_timing_zzy'):
                        global group_id_zzy
                        group_id_zzy = chatroom.get('UserName')
                        break
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            if self.useHotReload:
                self.dump_login_status()
            self.alive = False
            logger.debug('itchat received an ^C and exit.')
            logger.info('Bye~')

    replyThread = threading.Thread(target=reply_fn_timing_zzy)
    replyThread.setDaemon(True)
    replyThread.start()

    if blockThread:
        reply_fn()
