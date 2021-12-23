from brownie import Lottery, config, network, exceptions
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract, fund_with_link
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
import pytest
import time

def skip_local():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

def test_can_pick_winner():
    skip_local()
    # Arrange
    account = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    # Act
    ending_lottery_tx = lottery.endLottery({"from": account})
    ending_lottery_tx.wait(1)
    time.sleep(180)
    # Assert
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
