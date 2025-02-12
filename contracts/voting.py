# State Variables
owner = Variable()
current_proposal_id = Variable()  # Track the current proposal ID
proposals = Hash(default_value=None)
proposal_votes = Hash(default_value=None)  # Stores voter choices by proposal_id and voter
proposal_voters = Hash(default_value=None)  # Stores voter addresses by proposal_id and index
proposal_vote_counts = Hash(default_value=0)  # Stores number of voters per proposal
proposal_metrics = Hash(default_value=0)  # Stores vote counts and power metrics for proposals

# Events for tracking contract operations
ProposalCreatedEvent = LogEvent(
    event="ProposalCreated",
    params={
        "proposal_id": {'type': str, 'idx': True},
        "creator": {'type': str, 'idx': True},
        "title": {'type': str},
        "expires_at": {'type': str},
        "metadata": {'type': str}
    }
)

VoteEvent = LogEvent(
    event="Vote",
    params={
        "proposal_id": {'type': str, 'idx': True},
        "voter": {'type': str, 'idx': True},
        "choice": {'type': str},
        "previous_choice": {'type': str}
    }
)

ProposalFinalizedEvent = LogEvent(
    event="ProposalFinalized",
    params={
        "proposal_id": {'type': str, 'idx': True},
        "total_for": {'type': int},
        "total_against": {'type': int},
        "total_abstain": {'type': int},
        "pow_for": {'type': (int, float)},
        "pow_against": {'type': (int, float)},
        "pow_abstain": {'type': (int, float)}
    }
)

# Configurable parameters stored in a settings hash
settings = Hash(default_value=None)

"""
TO DO :
- add a max length for a title (10-50 characters)
- make max / min parameters that can be changed by the owner.
- add a fee for creating a proposal, it must a changeable value by the owner
"""


@construct
def seed():
    """
    Initialize the contract with the deployer as the owner
    """
    owner.set(ctx.caller)
    current_proposal_id.set(0)  # Initialize proposal ID counter
    
    # Initialize configurable parameters with default values
    settings["min_title_length"] = 10  # Default minimum title length
    settings["max_title_length"] = 50  # Default maximum title length
    settings["proposal_fee"] = 100  # Default proposal fee in currency tokens
    settings["auto_update_tallies"] = False  # Default to false for gas efficiency


@export
def change_owner(new_owner: str):
    """
    Change the contract owner
    """
    assert ctx.caller == owner.get(), "Only owner can change owner"
    owner.set(new_owner)


@export
def update_settings(setting_name: str, value: Any):
    """
    Update a contract setting
    Args:
        setting_name: Name of the setting to update
        value: New value for the setting
    """
    assert ctx.caller == owner.get(), "Only owner can change settings"
    
    if setting_name == "title_length_limits":
        assert isinstance(value, list) and len(value) == 2, "Title length limits must be a list of [min, max]"
        min_length, max_length = value
        assert isinstance(min_length, int) and isinstance(max_length, int), "Lengths must be integers"
        assert 0 < min_length <= max_length, "Invalid length values"
        settings["min_title_length"] = min_length
        settings["max_title_length"] = max_length
    
    elif setting_name == "proposal_fee":
        assert isinstance(value, int) and value >= 0, "Fee must be a non-negative integer"
        settings["proposal_fee"] = value
    
    elif setting_name == "auto_update_tallies":
        assert isinstance(value, int), "Auto update tallies must be an integer"
        settings["auto_update_tallies"] = value
    
    else:
        raise Exception("Invalid setting name")


@export
def get_settings():
    """
    Get the current contract settings
    """
    return {
        "min_title_length": settings["min_title_length"],
        "max_title_length": settings["max_title_length"],
        "proposal_fee": settings["proposal_fee"],
        "auto_update_tallies": settings["auto_update_tallies"]
    }


@export
def create_proposal(title: str, description: str, expires_at: str, metadata: dict = None):
    """
    Create a new proposal
    Args:
        title: Title of the proposal (length must be between min_title_length and max_title_length)
        description: Detailed description of the proposal (minimum 100 characters)
        expires_at: Datetime string in format 'YYYY-MM-DD HH:MM:SS'
        metadata: Optional dictionary of key-value pairs for additional proposal data
    """

    # Check if creator has tokens

    # Type checking
    assert isinstance(title, str), "Title must be a string"
    assert isinstance(description, str), "Description must be a string"
    assert isinstance(expires_at, str), "Expiry date must be a string"
    if metadata is not None:
        assert isinstance(metadata, dict), "Metadata must be a dictionary"
        for key, value in metadata.items():
            assert isinstance(key, str), "Metadata keys must be strings"
            assert isinstance(value, (str, int, bool, float)), "Metadata values must be primitive types"

    # Length checking
    assert title != "", "Title cannot be empty"
    title_len = len(title)
    assert title_len >= settings["min_title_length"], f"Title must be at least {settings['min_title_length']} characters long"
    assert title_len <= settings["max_title_length"], f"Title must be at most {settings['max_title_length']} characters long"
    assert description != "", "Description cannot be empty"
    assert len(description) >= 100, "Description must be at least 100 characters long"

    # Convert string to datetime for storage and comparison
    expiry_datetime = datetime.datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
    assert expiry_datetime > now, "Expiry date must be in the future"

    # Handle proposal fee
    proposal_fee = settings["proposal_fee"]
    if proposal_fee > 0:
        # Transfer fee using the currency contract
        currency = importlib.import_module('currency')
        currency.transfer_from(amount=proposal_fee, to='dao', main_account=ctx.caller)

    # Get and increment the proposal ID
    proposal_id = current_proposal_id.get()
    current_proposal_id.set(proposal_id + 1)

    # Store proposal details
    proposals[proposal_id] = {
        "title": title,
        "description": description,
        "creator": ctx.caller,
        "created_at": now,
        "expires_at": expiry_datetime,
        "status": "active",
        "fee_paid": proposal_fee,
        "metadata": metadata or {}  # Store empty dict if no metadata provided
    }
    
    # Initialize vote count
    proposal_vote_counts[proposal_id] = 0
    
    # Initialize vote tallies and power in proposal_metrics
    proposal_metrics[proposal_id, "total_for"] = 0
    proposal_metrics[proposal_id, "total_against"] = 0
    proposal_metrics[proposal_id, "total_abstain"] = 0
    proposal_metrics[proposal_id, "pow_for"] = 0
    proposal_metrics[proposal_id, "pow_against"] = 0
    proposal_metrics[proposal_id, "pow_abstain"] = 0

    # Emit proposal created event
    ProposalCreatedEvent({
        "proposal_id": str(proposal_id),
        "creator": ctx.caller,
        "title": title,
        "expires_at": expires_at,
        "metadata": str(metadata) or str({})
    })

    return proposal_id


@export
def vote(proposal_id: str, choice: str):
    """
    Vote on a proposal or change an existing vote
    Args:
        proposal_id: The ID of the proposal
        choice: Vote choice - 'y' for yes, 'n' for no, '-' for abstain
    """
    # Check if proposal exists and is active
    proposal = proposals[proposal_id]
    assert proposal is not None, "Proposal does not exist"
    assert proposal["status"] == "active", "Proposal is not active"
    assert now <= proposal["expires_at"], "Proposal voting period has ended"
    assert choice in ["y", "n", "-"], "Invalid vote choice. Must be 'y', 'n', or '-'"

    # Get current vote if exists
    current_vote = proposal_votes[proposal_id, ctx.caller]
    
    # If changing vote, verify it's different
    if current_vote is not None:
        assert current_vote != choice, "New vote must be different from current vote"
    else:
        # New vote - increment vote count and store voter
        current_vote_count = proposal_vote_counts[proposal_id]
        proposal_voters[proposal_id, current_vote_count] = ctx.caller
        proposal_vote_counts[proposal_id] = current_vote_count + 1

    # Store the vote
    proposal_votes[proposal_id, ctx.caller] = choice

    # Emit vote event
    VoteEvent({
        "proposal_id": str(proposal_id),
        "voter": ctx.caller,
        "choice": choice,
        "previous_choice": current_vote if current_vote else ""
    })

    # Update tallies if auto-update is enabled
    if settings["auto_update_tallies"] > 0:
        update_current_tallies(proposal_id)


def tally_current_votes(proposal_id: str):
    """
    Private method to calculate current vote counts and power
    Returns both raw vote counts and power-weighted totals
    Only counts votes from users who currently hold tokens
    """
    token_balances = ForeignHash(foreign_contract="currency", foreign_name="balances")
    
    total_for = 0
    total_against = 0
    total_abstain = 0
    pow_for = 0
    pow_against = 0
    pow_abstain = 0

    voter_count = proposal_vote_counts[proposal_id]
    for i in range(voter_count):
        voter = proposal_voters[proposal_id, i]
        vote = proposal_votes[proposal_id, voter]
        voter_weight = token_balances[voter]

        # Only count votes from users who still have tokens
        if voter_weight > 0:
            if vote == "y":
                total_for += 1
                pow_for += voter_weight
            elif vote == "n":
                total_against += 1
                pow_against += voter_weight
            else:  # vote == '-'
                total_abstain += 1
                pow_abstain += voter_weight

    return {
        "for": total_for,
        "against": total_against,
        "abstain": total_abstain,
        "pow_for": pow_for,
        "pow_against": pow_against,
        "pow_abstain": pow_abstain
    }


@export
def finalize_proposal(proposal_id: str):
    """
    Calculate final vote tallies after proposal expiry using current token balances
    """
        
    proposal = proposals[proposal_id]
    assert proposal is not None, "Proposal does not exist"
    assert now > proposal["expires_at"], "Proposal voting period has not ended"
    assert proposal["status"] == "active", "Proposal already finalized"

    # Get final vote tallies
    final_tally = tally_current_votes(proposal_id)

    # Store final tallies in proposal_metrics
    proposal_metrics[proposal_id, "total_for"] = final_tally["for"]
    proposal_metrics[proposal_id, "total_against"] = final_tally["against"]
    proposal_metrics[proposal_id, "total_abstain"] = final_tally["abstain"]
    proposal_metrics[proposal_id, "pow_for"] = final_tally["pow_for"]
    proposal_metrics[proposal_id, "pow_against"] = final_tally["pow_against"]
    proposal_metrics[proposal_id, "pow_abstain"] = final_tally["pow_abstain"]

    # Update proposal status
    proposal["status"] = "finalized"
    proposals[proposal_id] = proposal

    # Emit finalized event
    ProposalFinalizedEvent({
        "proposal_id": str(proposal_id),
        "total_for": final_tally["for"],
        "total_against": final_tally["against"],
        "total_abstain": final_tally["abstain"],
        "pow_for": final_tally["pow_for"],
        "pow_against": final_tally["pow_against"],
        "pow_abstain": final_tally["pow_abstain"]
    })

    return final_tally


@export
def get_proposal(proposal_id: str):
    """
    Get proposal details including current metrics
    """
    proposal = proposals[proposal_id]
    assert proposal is not None, "Proposal does not exist"
    
    # Add metrics to the proposal data
    proposal_data = {
        **proposal,
        "total_for": proposal_metrics[proposal_id, "total_for"],
        "total_against": proposal_metrics[proposal_id, "total_against"],
        "total_abstain": proposal_metrics[proposal_id, "total_abstain"],
        "pow_for": proposal_metrics[proposal_id, "pow_for"],
        "pow_against": proposal_metrics[proposal_id, "pow_against"],
        "pow_abstain": proposal_metrics[proposal_id, "pow_abstain"]
    }
    
    return proposal_data


@export
def get_vote_count(proposal_id: str):
    """
    Get the current vote count for a proposal
    """
    proposal = proposals[proposal_id]
    assert proposal is not None, "Proposal does not exist"

    if proposal["status"] == "finalized":
        return {
            "for": proposal_metrics[proposal_id, "total_for"],
            "against": proposal_metrics[proposal_id, "total_against"],
            "abstain": proposal_metrics[proposal_id, "total_abstain"],
            "pow_for": proposal_metrics[proposal_id, "pow_for"],
            "pow_against": proposal_metrics[proposal_id, "pow_against"],
            "pow_abstain": proposal_metrics[proposal_id, "pow_abstain"]
        }
    else:
        # Get current vote counts and power
        current_tally = tally_current_votes(proposal_id)
        return current_tally


@export
def update_current_tallies(proposal_id: str):
    """
    Calculate and update current vote tallies in the proposal hash
    Returns the current tallies
    """
    token_balances = ForeignHash(foreign_contract="currency", foreign_name="balances")
    
    # Check if caller has tokens
    assert token_balances[ctx.caller] > 0, "Must have tokens to update tallies"
    
    proposal = proposals[proposal_id]
    assert proposal is not None, "Proposal does not exist"
    assert proposal["status"] == "active", "Proposal is not active"

    # Get current tallies
    current_tally = tally_current_votes(proposal_id)

    # Update proposal tallies in proposal_metrics
    proposal_metrics[proposal_id, "total_for"] = current_tally["for"]
    proposal_metrics[proposal_id, "total_against"] = current_tally["against"]
    proposal_metrics[proposal_id, "total_abstain"] = current_tally["abstain"]
    proposal_metrics[proposal_id, "pow_for"] = current_tally["pow_for"]
    proposal_metrics[proposal_id, "pow_against"] = current_tally["pow_against"]
    proposal_metrics[proposal_id, "pow_abstain"] = current_tally["pow_abstain"]

    return current_tally
