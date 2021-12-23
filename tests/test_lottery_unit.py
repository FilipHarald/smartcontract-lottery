from brownie import Lottery, config, network, exceptions
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract, fund_with_link
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
import pytest
import time

def skip_local():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

def test_get_entrance_fee():
    skip_local()
    # Arrange
    lottery = deploy_lottery()
    # Act
    expected_entrance_fee = lottery.getEntranceFee();
    # Assert
    assert expected_entrance_fee ==  Web3.toWei(0.025, "ether")

def test_cant_enter_if_not_started():
    skip_local()
    # Arrange
    account = get_account()
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": account, "value": lottery.getEntranceFee()})

def test_can_start_and_enter_lottery():
    skip_local()
    # Arrange
    account = get_account()
    lottery = deploy_lottery()
    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account

def test_can_end_lottery():
    skip_local()
    # Arrange
    account = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    # Act
    lottery.endLottery({"from": account})
    # Assert
    assert lottery.lottery_state() == 2

def test_can_pick_winner_correctly():
    skip_local()
    # Arrange
    account = get_account()
    lottery = deploy_lottery()
    entrance_fee = lottery.getEntranceFee()
    lottery.startLottery({"from": account})
    players = [get_account(index=1), get_account(index=2), get_account(index=3)]
    for playerAccount in players:
        lottery.enter({"from": playerAccount, "value": entrance_fee})
    fund_with_link(lottery)
    STATIC_RANDOM_NBR = 4
    selected_winner = players[STATIC_RANDOM_NBR % len(players)]
    winner_init_balance = selected_winner.balance()
    lottery_init_balance = lottery.balance()
    # Act
    ending_lottery_tx = lottery.endLottery({"from": account})
    request_id = ending_lottery_tx.events["RequestedRandomness"]["requestId"]
    get_contract("vrf_coordinator").callBackWithRandomness(request_id, STATIC_RANDOM_NBR, lottery.address, {"from": account})
    # Assert
    assert lottery.recentWinner() == selected_winner
    assert lottery.balance() == 0
    assert selected_winner.balance() == winner_init_balance + lottery_init_balance
