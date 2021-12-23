from brownie import Lottery, network, config
from scripts.helpful_scripts import get_account, get_contract, fund_with_link
import time

def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()].get("randomnessFee"),
        config["networks"][network.show_active()].get("keyhash"),
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False)
    )
    print(f"Deployed lottery!")
    return lottery

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    lottery_starting_tx = lottery.startLottery({"from": account})
    lottery_starting_tx.wait(1)
    print("The lottery has started!")

def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    entering_tx = lottery.enter({"from": account, "value": value})
    entering_tx.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    fund_with_link(lottery.address)
    print("ending lottery...")
    ending_lottery_tx = lottery.endLottery({"from": account})
    print("ending started...")
    ending_lottery_tx.wait(1)
    time.sleep(180)
    print(f"Aaaaand the winner iiiis....: {lottery.recentWinner()}")

def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
