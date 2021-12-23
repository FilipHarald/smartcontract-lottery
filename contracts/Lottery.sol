// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is VRFConsumerBase, Ownable {
  address payable[] public players;
  address payable public recentWinner;
  uint256 public randomness;
  uint256 public usdEntryFee;
  AggregatorV3Interface internal ethUsdPriceFeed;
  enum LOTTERY_STATE {
    OPEN,
    CLOSED,
    CALCULATING_WINNER
  }
  LOTTERY_STATE public lottery_state;
  uint256 public randomessFee;
  bytes32 public keyhash;
  event RequestedRandomness(bytes32 requestId);

  constructor(
    address _priceFeedAddress,
    address _vrfCoordinator,
    address _link,
    uint256 _randomessFee,
    bytes32 _keyhash
  )
  public
  VRFConsumerBase(
    _vrfCoordinator,
    _link
  ) {
    usdEntryFee = 50 * (10**18);
    ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
    lottery_state = LOTTERY_STATE.CLOSED;
    randomessFee = _randomessFee;
    keyhash = _keyhash;
  }

  function enter() public payable {
    require(lottery_state == LOTTERY_STATE.OPEN);
    require(msg.value >= getEntranceFee(), "Not enough ETH!");
    players.push(msg.sender);
  }

  function getEntranceFee() public view returns (uint256) {
    (,int price,,,) = ethUsdPriceFeed.latestRoundData();
    uint256 adjustedPrice = uint256(price) * 10 **10;
    uint256 costToEnter = (usdEntryFee * 10 ** 18) / adjustedPrice;
    return costToEnter;
  }

  function startLottery() public onlyOwner {
    require(lottery_state == LOTTERY_STATE.CLOSED, "Cant start a new lottery yet!");
    lottery_state = LOTTERY_STATE.OPEN;
  }

  function endLottery() public onlyOwner {
    require(lottery_state == LOTTERY_STATE.OPEN, "Cant stop lottery at the moment!");
    lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
    bytes32 requestId = requestRandomness(keyhash, randomessFee);
    emit RequestedRandomness(requestId);
  }

  function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override {
    require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER, "You arnt there yet!");
    require(_randomness > 0, "random-not-found");
    recentWinner = players[_randomness % players.length];
    recentWinner.transfer(address(this).balance);
    players = new address payable [](0);
    lottery_state = LOTTERY_STATE.CLOSED;
    randomness = _randomness;
  }
}
