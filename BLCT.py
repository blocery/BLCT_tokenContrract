OntCversion = '2.0.0'
"""
An Example of OEP-4
"""
from ontology.interop.System.Storage import GetContext, Get, Put, Delete
from ontology.interop.System.Runtime import Notify, CheckWitness,GetTime, Serialize, Deserialize
from ontology.interop.System.Action import RegisterAction
from ontology.builtins import concat
from ontology.interop.Ontology.Runtime import Base58ToAddress
from ontology.interop.System.Runtime import GetTime, Notify, Serialize, Deserialize


TransferEvent = RegisterAction("transfer", "from", "to", "amount")
ApprovalEvent = RegisterAction("approval", "owner", "spender", "amount")
ContractPauseEvent = RegisterAction("contractPause", "state")
UserFreezeEvent = RegisterAction("userFreeze", "owner", "state")
TransferOwnershipEvent = RegisterAction("transferOwnership", "previousOwner", "newOwner")

ctx = GetContext()

NAME = 'Blocery Token[BLCT]'
SYMBOL = 'BLCT'
DECIMALS = 8
FACTOR = 100000000
INITOWNER = Base58ToAddress("AYZ14K5FJKXC9mzS5YFfdr52E6seBqAPPU")

TOTAL_AMOUNT = 1000000000
BALANCE_PREFIX = bytearray(b'\x01')
APPROVE_PREFIX = b'\x02'
USER_FREEZE_PREFIX = b'\x03'

USER_LOCK_PREFIX =  b'\x04'
USER_LOCK_CNT_PREFIX =  b'\x05'

SUPPLY_KEY = 'TotalSupply'
CONTRACT_PAUSE_KEY = 'PauseContract'
OWNER_KEY = 'Owner'

def Main(operation, args):
    """
    :param operation:
    :param args:
    :return:
    """
    # 'init' has to be invokded first after deploying the contract to store the necessary and important info in the blockchain
    if operation == 'init':
        return init()
    if operation == 'name':
        return name()
    if operation == 'symbol':
        return symbol()
    if operation == 'decimals':
        return decimals()
    if operation == 'totalSupply':
        return totalSupply()
    if operation == 'balanceOf':
        if len(args) != 1:
            return False
        acct = args[0]
        return balanceOf(acct)
    if operation == 'transfer':
        if len(args) != 3:
            return False
        else:
            from_acct = args[0]
            to_acct = args[1]
            amount = args[2]
            return transfer(from_acct,to_acct,amount)
    if operation == 'transferMulti':
        return transferMulti(args)
    if operation == 'transferFrom':
        if len(args) != 4:
            return False
        spender = args[0]
        from_acct = args[1]
        to_acct = args[2]
        amount = args[3]
        return transferFrom(spender,from_acct,to_acct,amount)
    if operation == 'approve':
        if len(args) != 3:
            return False
        owner  = args[0]
        spender = args[1]
        amount = args[2]
        return approve(owner,spender,amount)
    if operation == 'allowance':
        if len(args) != 2:
            return False
        owner = args[0]
        spender = args[1]
        return allowance(owner,spender)
    if operation == 'owner':
        return owner()
    if operation == 'isOwner':
        if len(args) != 1:
            return False
        acct = args[0]
        return isOwner(acct)
    if operation == "transferOwnership":
        if len(args) != 1:
            return False
        acct = args[0]
        return transferOwnership(acct)
    if operation == 'pause':
        return pause()
    if operation == 'unpause':
        return unpause()
    if operation == 'viewPause':
        return viewPause()
    if operation == 'freezeAccount':
        if len(args) != 1:
            return False
        acct = args[0]
        return freezeAccount(acct)
    if operation == 'unfreezeAccount':
        if len(args) != 1:
            return False
        acct = args[0]
        return unfreezeAccount(acct)
    if operation == 'viewFreezeAccount':
        if len(args) != 1:
            return False
        acct= args[0]
        return viewFreezeAccount(acct)
    if operation == 'lock':
        if len(args) != 3:
            return False
        holder = args[0]
        time = args[1]
        value = args[2]
        return lock(holder, time, value)
    if operation == 'unlock':
        onlyOwner()
        holder = args[0]
        idx = args[1]
        return unlock(holder, idx)
    if operation == 'getLockCount':
        holder = args[0]
        return getLockCount(holder)
    if operation == 'getLockState':
        holder = args[0]
        idx = args[1]
        return getLockState(holder, idx)
    if operation == 'getLockStateTime':
        holder = args[0]
        idx = args[1]
        return getLockStateTime(holder, idx)
    if operation == 'getLockStateAmount':
        holder = args[0]
        idx = args[1]
        return getLockStateAmount(holder, idx)
    if operation == 'autoUnlock':
        holder = args[0]
        return autoUnlock(holder)
    if operation == 'transferableBalanceOf':
        if len(args) != 1:
            return False
        acct = args[0]
        return transferableBalanceOf(acct)
    if operation == 'lockedBalanceOf':
        if len(args) != 1:
            return False
        acct = args[0]
        return lockedBalanceOf(acct)
    return False

def init():
    """
    initialize the contract, put some important info into the storage in the blockchain
    :return:
    """
    require(len(INITOWNER) == 20, "Owner illegal!" )
    
    Put(ctx, OWNER_KEY, INITOWNER)    
    OWNER = Get(ctx, OWNER_KEY)
    
    require(Get(ctx, SUPPLY_KEY) == False, "Already initialized")
    
    total = TOTAL_AMOUNT * FACTOR
    Put(ctx,SUPPLY_KEY,total)
    Put(ctx,concat(BALANCE_PREFIX,OWNER),total)

    TransferEvent("", OWNER, total)
    TransferOwnershipEvent("", OWNER)

    return True


def name():
    """
    :return: name of the token
    """
    return NAME


def symbol():
    """
    :return: symbol of the token
    """
    return SYMBOL


def decimals():
    """
    :return: the decimals of the token
    """
    return DECIMALS


def totalSupply():
    """
    :return: the total supply of the token
    """
    return Get(ctx, SUPPLY_KEY)


def balanceOf(account):
    """
    :param account:
    :return: the token balance of account
    """
    require(len(account) == 20, "address length error")
    
    return transferableBalanceOf(account) + lockedBalanceOf(account)

def transferableBalanceOf(account):
    require(len(account) == 20, "address length error")
    return Get(ctx,concat(BALANCE_PREFIX,account))

def lockedBalanceOf(account):
    KEY_lockCount = concat(USER_LOCK_CNT_PREFIX, account)
    lockCount = Get(ctx, KEY_lockCount)
    
    lockedAmont = 0
    if lockCount > 0:
        for i in range(0, lockCount):
            lockinfo = getLockState(account,i)
            deserializeUserLock = Deserialize(lockinfo)
            releaseAmount = deserializeUserLock['releaseAmount']
            lockedAmont+=releaseAmount
    return lockedAmont

def transfer(from_acct,to_acct,amount):
    """
    Transfer amount of tokens from from_acct to to_acct
    :param from_acct: the account from which the amount of tokens will be transferred
    :param to_acct: the account to which the amount of tokens will be transferred
    :param amount: the amount of the tokens to be transferred, >= 0
    :return: True means success, False or raising exception means failure.
    """
    require(len(to_acct) == 20 and len(from_acct) == 20, "address length error")
    require(CheckWitness(from_acct) == True, "Invalid invoker")
    require(amount > 0, "Invalid Amount")

    whenNotPaused()
    requireNotFreeze(from_acct)
    requireNotFreeze(to_acct)
    
    # if from_acct has lockinfo, it will be unlock
    autoUnlock(from_acct)

    fromKey = concat(BALANCE_PREFIX,from_acct)
    fromBalance = Get(ctx,fromKey)
    
    require(amount <= fromBalance, "Not enough balance")

    if amount == fromBalance:
        Delete(ctx,fromKey)
    else:
        Put(ctx,fromKey,fromBalance - amount)

    toKey = concat(BALANCE_PREFIX,to_acct)
    toBalance = Get(ctx,toKey)
    Put(ctx,toKey,toBalance + amount)

    # Notify(["transfer", AddressToBase58(from_acct), AddressToBase58(to_acct), amount])
    # TransferEvent(AddressToBase58(from_acct), AddressToBase58(to_acct), amount)
    TransferEvent(from_acct, to_acct, amount)

    return True


def transferMulti(args):
    """
    :param args: the parameter is an array, containing element like [from, to, amount]
    :return: True means success, False or raising exception means failure.
    """
    for p in args:
        if len(p) != 3:
            # return False is wrong
            raise Exception("transferMulti params error.")
        require(transfer(p[0], p[1], p[2]), "transferMulti failed")

    return True


def approve(owner,spender,amount):
    """
    owner allow spender to spend amount of token from owner account
    Note here, the amount should be less than the balance of owner right now.
    :param owner:
    :param spender:
    :param amount: amount>=0
    :return: True means success, False or raising exception means failure.
    """
    require(len(spender) == 20 and len(owner) == 20, "address length error")
    require(CheckWitness(owner) == True, "Invalid invoker")
    require(amount > 0, "Invalid amount")

    key = concat(concat(APPROVE_PREFIX,owner),spender)
    Put(ctx, key, amount)

    # Notify(["approval", AddressToBase58(owner), AddressToBase58(spender), amount])
    # ApprovalEvent(AddressToBase58(owner), AddressToBase58(spender), amount)
    ApprovalEvent(owner, spender, amount)

    return True


def transferFrom(spender,from_acct,to_acct,amount):
    """
    spender spends amount of tokens on the behalf of from_acct, spender makes a transaction of amount of tokens
    from from_acct to to_acct
    :param spender:
    :param from_acct:
    :param to_acct:
    :param amount:
    :return:
    """
    require(len(spender) == 20 and len(from_acct) == 20 and len(to_acct) == 20, "address length error")
    require(CheckWitness(spender) == True, "Invalid invoker")

    whenNotPaused()
    requireNotFreeze(spender)
    requireNotFreeze(from_acct)
    requireNotFreeze(to_acct)
    
    autoUnlock(from_acct)
    
    fromKey = concat(BALANCE_PREFIX, from_acct)
    fromBalance = Get(ctx, fromKey)
    require(amount <= fromBalance and amount > 0, "Invalid amount")

    approveKey = concat(concat(APPROVE_PREFIX,from_acct),spender)
    approvedAmount = Get(ctx,approveKey)
    toKey = concat(BALANCE_PREFIX,to_acct)
    
    require(amount <= approvedAmount, "Invalid amount")

    if amount == approvedAmount:
        Delete(ctx,approveKey)
        Put(ctx, fromKey, fromBalance - amount)
    else:
        Put(ctx,approveKey,approvedAmount - amount)
        Put(ctx, fromKey, fromBalance - amount)

    toBalance = Get(ctx, toKey)
    Put(ctx, toKey, toBalance + amount)

    # Notify(["transfer", AddressToBase58(from_acct), AddressToBase58(to_acct), amount])
    # TransferEvent(AddressToBase58(from_acct), AddressToBase58(to_acct), amount)
    TransferEvent(from_acct, to_acct, amount)

    return True


def allowance(owner,spender):
    """
    check how many token the spender is allowed to spend from owner account
    :param owner: token owner
    :param spender:  token spender
    :return: the allowed amount of tokens
    """
    key = concat(concat(APPROVE_PREFIX,owner),spender)
    return Get(ctx,key)
    
def owner():
    return Get(ctx, OWNER_KEY)
    
def isOwner(account):
    if (Get(ctx, OWNER_KEY) == account):
        return True
    else:
        return False

def transferOwnership(account):
    onlyOwner()
    require(len(account) == 20, "address length error")
        
    previousOwner = Get(ctx, OWNER_KEY)
    
    Put(ctx, OWNER_KEY, account)
    
    TransferOwnershipEvent(previousOwner, account)
    return True

def onlyOwner():
    require(CheckWitness(Get(ctx, OWNER_KEY)), "Not Owner")
    
def require(condition,msg):
    if not condition:
        raise Exception(msg)
    return True
    
def pause():
    onlyOwner()
    whenNotPaused()
    Put(ctx, CONTRACT_PAUSE_KEY, True)
    ContractPauseEvent(True)
    return True

def unpause():
    onlyOwner()
    whenPaused()
    Put(ctx, CONTRACT_PAUSE_KEY, False)
    ContractPauseEvent(False)
    return True
    
def viewPause():
    return Get(ctx, CONTRACT_PAUSE_KEY)
    
def whenNotPaused():
    require(Get(ctx, CONTRACT_PAUSE_KEY) == False, "Not pause state of Contract")

def whenPaused():
    require(Get(ctx, CONTRACT_PAUSE_KEY) == True, "Not unpause state of Contract")

def freezeAccount(account):
    onlyOwner()
    requireNotFreeze(account)
    require(len(account) == 20, "address length error")
    Put(ctx, concat(USER_FREEZE_PREFIX, account), True)
    UserFreezeEvent(account, True)
    return True

def unfreezeAccount(account):
    onlyOwner()
    requireFreeze(account)
    require(len(account) == 20, "address length error")
    Put(ctx, concat(USER_FREEZE_PREFIX, account), False)
    UserFreezeEvent(account, False)
    return True
    
def viewFreezeAccount(account):
    return Get(ctx, concat(USER_FREEZE_PREFIX, account))

def requireNotFreeze(account):
    require(Get(ctx, concat(USER_FREEZE_PREFIX, account)) == False, "Not unfrozen state of account")
    
def requireFreeze(account):
    require(Get(ctx, concat(USER_FREEZE_PREFIX, account)) == True, "Not frozen state of account")

def getLockState(account, idx):
    KEY_lockInfo = concat(concat(USER_LOCK_PREFIX, account), idx)
    lockInfo = Get(ctx, KEY_lockInfo)
    return lockInfo

def getLockStateTime(account, idx):
    KEY_lockInfo = concat(concat(USER_LOCK_PREFIX, account), idx)
    lockInfo = Get(ctx, KEY_lockInfo)
    deserializeUserLock = Deserialize(lockInfo)
    releaseTime = deserializeUserLock['releaseTime']
    return releaseTime
    
def getLockStateAmount(account, idx):
    KEY_lockInfo = concat(concat(USER_LOCK_PREFIX, account), idx)
    lockInfo = Get(ctx, KEY_lockInfo)
    deserializeUserLock = Deserialize(lockInfo)
    releaseAmount = deserializeUserLock['releaseAmount']
    return releaseAmount
    
def getLockCount(holder): 
    lockCountKey = concat(USER_LOCK_CNT_PREFIX, holder)
    lockCount = Get(ctx, lockCountKey)
    return lockCount

def lock(account, time, amount):
    # Permission Check
    onlyOwner()
    
    # Lockup amount must be smaller then real balance
    balance = Get(ctx,concat(BALANCE_PREFIX,account))
    require(amount <= balance,"lock amount is bigger than balance")
    
    # Sub amount from Balance
    Put(ctx,concat(BALANCE_PREFIX,account), balance-amount)
    
    # Get User's count of lockinfo
    KEY_lockCount = concat(USER_LOCK_CNT_PREFIX, account)
    lockCount = Get(ctx, KEY_lockCount)
    
    KEY_lockInfo = concat(concat(USER_LOCK_PREFIX, account), lockCount)

    # Create Lockup Information
    setLock = {
        "releaseTime": time, 
        "releaseAmount": amount,
    }
    serializeSetLock = Serialize(setLock)
    
    # Store lockInfo & increase count
    Put(ctx, KEY_lockInfo, serializeSetLock)
    Put(ctx, KEY_lockCount, lockCount+1)
    
    Notify([serializeSetLock])
    return True

def unlock(account, idx):
    KEY_lockCount = concat(USER_LOCK_CNT_PREFIX, account)
    lockCount = Get(ctx, KEY_lockCount)
    
    # idx is smaller than count of lock
    # require(idx<lockCount,"idx out of range")
    if idx>=lockCount:
        return False

    # Get lock info and releaseAmount
    KEY_lockInfo = concat(concat(USER_LOCK_PREFIX, account), idx)
    serializedLockinfo = Get(ctx, KEY_lockInfo)
    lockInfo = Deserialize(serializedLockinfo)
    
    releaseAmount = lockInfo['releaseAmount']
    releaseTime = lockInfo['releaseTime']
    
    # releaseAmount is Added to balance
    balance = Get(ctx,concat(BALANCE_PREFIX,account))
    Put(ctx,concat(BALANCE_PREFIX,account), balance+releaseAmount)
    
    # last lockinfo copy to this idx
    lastLockInfo = Get(ctx, concat(concat(USER_LOCK_PREFIX, account),lockCount-1))
    Put(ctx, KEY_lockInfo, lastLockInfo)
    
    # delete last lockinfo (duplicated)
    Delete(ctx, concat(concat(USER_LOCK_PREFIX, account),lockCount-1))
    
    # decrease lockup count 
    Put(ctx, KEY_lockCount, lockCount - 1)
    
    Notify([releaseTime,releaseAmount])
    return True
    
def autoUnlock(account):
    now = GetTime()
    
    KEY_lockCount = concat(USER_LOCK_CNT_PREFIX, account)
    lockCount = Get(ctx, KEY_lockCount)
    
    if lockCount > 0:
        i=0
        while i < lockCount:
            lockInfo = getLockState(account,i)
            deserializeUserLock = Deserialize(lockInfo)
            releaseTime = deserializeUserLock['releaseTime']
            Notify([releaseTime])

            if releaseTime <= now:
                if unlock(account, i):
                    i -= 1
                    lockCount -=1
            i+=1
            
               
    return True
