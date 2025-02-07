// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title TrafficViolation
 * @dev A smart contract to log and validate traffic violations.
 */
contract TrafficViolation {
    /// @dev Structure to store violation details.
    struct Violation {
        uint id;                    // Unique identifier for the violation
        string location;             // Location where the violation occurred
        uint timestamp;              // Timestamp of when the violation was recorded
        string videoRef;             // Reference to the video evidence of the violation
        string vehicleRegNo;         // Vehicle registration number involved in the violation
        string driverLicenseNo;      // Driver’s license number of the violator
        bool validated;              // Status indicating whether the violation has been validated by the admin
    }

    address public admin;            // Address of the admin who can validate violations
    uint public violationCount;      // Counter to keep track of total violations recorded
    mapping(uint => Violation) public violations;  // Mapping to store violations with their unique ID

    /// @dev Event emitted when a new violation is logged.
    event ViolationLogged(
        uint id,
        string location,
        uint timestamp,
        string videoRef,
        string vehicleRegNo,
        string driverLicenseNo
    );

    /// @dev Event emitted when a violation is validated.
    event ViolationValidated(uint id);

    /// @dev Modifier to restrict function access to the admin only.
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can validate violations");
        _;
    }

    /**
     * @dev Constructor sets the contract deployer as the admin.
     */
    constructor() {
        admin = msg.sender;
        violationCount = 0;
    }

    /**
     * @dev Logs a new traffic violation.
     * @param _location The location of the violation.
     * @param _videoRef Reference to the video evidence.
     * @param _vehicleRegNo Vehicle registration number.
     * @param _driverLicenseNo Driver’s license number.
     */
    function logViolation(
        string memory _location,
        string memory _videoRef,
        string memory _vehicleRegNo,
        string memory _driverLicenseNo
    ) public {
        violationCount++;
        violations[violationCount] = Violation(
            violationCount,
            _location,
            block.timestamp,
            _videoRef,
            _vehicleRegNo,
            _driverLicenseNo,
            false
        );

        emit ViolationLogged(violationCount, _location, block.timestamp, _videoRef, _vehicleRegNo, _driverLicenseNo);
    }

    /**
     * @dev Validates a traffic violation. Only the admin can perform this action.
     * @param _id The unique ID of the violation to be validated.
     */
    function validateViolation(uint _id) public onlyAdmin {
        violations[_id].validated = true;
        emit ViolationValidated(_id);
    }

    /**
     * @dev Retrieves a traffic violation record by its ID.
     * @param _id The unique ID of the violation.
     * @return The Violation struct corresponding to the given ID.
     */
    function getViolation(uint _id) public view returns (Violation memory) {
        return violations[_id];
    }
}
