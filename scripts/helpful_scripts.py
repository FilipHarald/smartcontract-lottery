from brownie import MockV3Aggregator, VRFCoordinatorMock, LinkToken, network, accounts, config, Contract, interface

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or
        network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken
}

def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
    return contract;

DECIMALS = 8
STARTING_PRICE = 200000000000

def deploy_mocks(decimals=DECIMALS, starting_price=STARTING_PRICE):
    account = get_account()
    print("Deploying mocks...")
    link_token = LinkToken.deploy({"from": account})
    MockV3Aggregator.deploy(decimals, starting_price, {"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Mocks deployed!")

def fund_with_link(contract_address, account=None, link_token=None, amount=100000000000000000): #0.1 LINK
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    print("Funding with LINK...")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # link_token_contract = interface.LinkTokenInterface(link _token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Contract funded!")
    return tx
