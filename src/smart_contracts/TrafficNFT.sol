// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title TrafficNFT
 * @dev A contract for minting NFTs representing traffic violations.
 * @notice This contract allows the owner to mint ERC721 tokens with metadata URIs.
 */
contract TrafficNFT is ERC721URIStorage, Ownable {
    uint256 private _tokenIdCounter; // Counter for tracking the next token ID

    /**
     * @dev Constructor initializes the ERC721 token with a name and symbol.
     * The contract owner is set during deployment.
     */
    constructor() ERC721("TrafficViolationNFT", "TVNFT") Ownable(msg.sender) {
        _tokenIdCounter = 0; // Initialize token counter
    }

    /**
     * @dev Mints a new NFT and assigns it to the specified address.
     * @notice Only the contract owner can call this function.
     * @param to The recipient address of the minted NFT.
     * @param tokenURI The metadata URI associated with the NFT.
     */
    function mintNFT(address to, string memory tokenURI) public onlyOwner {
        _tokenIdCounter++; // Increment token ID counter
        uint256 newItemId = _tokenIdCounter; // Assign new token ID

        _mint(to, newItemId); // Mint the NFT to the specified address
        _setTokenURI(newItemId, tokenURI); // Set the metadata URI for the NFT
    }
}
