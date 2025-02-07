# State Variables
owner = Variable()
proposals = Hash(default_value=None)
proposal_votes = Hash(default_value=None)  # Stores voter choices by proposal_id and voter
proposal_voters = Hash(default_value=None)  # Stores voter addresses by proposal_id and index
proposal_vote_counts = Hash(default_value=0)  # Stores number of voters per proposal
auto_update_tallies = Variable()
proposal_metrics = Hash(default_value=0)  # Stores vote counts and power metrics for proposals

"""
TO DO :
- Overall consolidate hash structure to proposal hash ✓
- Add property to proposal hash to show current vote count + power
- Add method that updates the count, power & tallies
- title should have a minimum length of 10 characters
- description should have a minimum length of 100 characters\
"""


@construct
def seed():
    """
    Initialize the contract with the deployer as the owner
    """
    owner.set(ctx.caller)
    auto_update_tallies.set(False)  # Default to false for gas efficiency


@export
def change_owner(new_owner: str):
    """
    Change the contract owner
    """
    assert ctx.caller == owner.get(), "Only owner can change owner"
    owner.set(new_owner)


@export
def create_proposal(title: str, description: str, expires_at: str):
    """
    Create a new proposal
    Args:
        title: Title of the proposal (minimum 10 characters)
        description: Detailed description of the proposal (minimum 100 characters)
        expires_at: Datetime string in format 'YYYY-MM-DD HH:MM:SS'
    """
    token_balances = ForeignHash(foreign_contract="currency", foreign_name="balances")
    
    # Check if creator has tokens
    assert token_balances[ctx.caller] > 0, "Must have tokens to create proposal"

    # Type checking
    assert isinstance(title, str), "Title must be a string"
    assert isinstance(description, str), "Description must be a string"
    assert isinstance(expires_at, str), "Expiry date must be a string"

    # Length checking
    assert title != "", "Title cannot be empty"
    assert len(title) >= 10, "Title must be at least 10 characters long"
    assert description != "", "Description cannot be empty"
    assert len(description) >= 100, "Description must be at least 100 characters long"

    # Convert string to datetime for storage and comparison
    expiry_datetime = datetime.datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
    assert expiry_datetime > now, "Expiry date must be in the future"

    # Create unique proposal ID using SHA3 hash
    proposal_id = hashlib.sha3(f"{title}{description}{ctx.caller}{now}")

    # Store proposal details
    proposals[proposal_id] = {
        "title": title,
        "description": description,
        "creator": ctx.caller,
        "created_at": now,
        "expires_at": expiry_datetime,
        "status": "active"
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

    return proposal_id


@export
def vote(proposal_id: str, choice: str):
    """
    Vote on a proposal - only records the voter's choice, weight calculated at finalization
    """
    token_balances = ForeignHash(foreign_contract="currency", foreign_name="balances")
    
    # Check if proposal exists
    proposal = proposals[proposal_id]
    assert proposal is not None, "Proposal does not exist"
    assert proposal["status"] == "active", "Proposal is not active"
    assert now <= proposal["expires_at"], "Proposal voting period has ended"
    assert choice in ["y", "n", "-"], "Invalid vote choice. Must be 'y', 'n', or '-'"

    # Check if voter has tokens
    assert token_balances[ctx.caller] > 0, "Must have tokens to vote"

    # Check if already voted
    assert proposal_votes[proposal_id, ctx.caller] is None, "Already voted"

    # Store vote
    current_vote_count = proposal_vote_counts[proposal_id]
    proposal_voters[proposal_id, current_vote_count] = ctx.caller
    proposal_votes[proposal_id, ctx.caller] = choice
    proposal_vote_counts[proposal_id] = current_vote_count + 1

    # Update tallies if auto-update is enabled
    if auto_update_tallies.get():
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


@export
def change_vote(proposal_id: str, new_choice: str):
    """
    Change an existing vote on a proposal
    Args:
        proposal_id: The ID of the proposal
        new_choice: New vote choice - 'y' for yes, 'n' for no, '-' for abstain
    """
    token_balances = ForeignHash(foreign_contract="currency", foreign_name="balances")
    
    # Check if proposal exists and is active
    proposal = proposals[proposal_id]
    assert proposal is not None, "Proposal does not exist"
    assert proposal["status"] == "active", "Proposal is not active"
    assert now <= proposal["expires_at"], "Proposal voting period has ended"
    assert new_choice in ["y", "n", "-"], "Invalid vote choice. Must be 'y', 'n', or '-'"

    # Check if voter has tokens
    assert token_balances[ctx.caller] > 0, "Must have tokens to vote"

    # Check if they have voted before
    assert proposal_votes[proposal_id, ctx.caller] is not None, "Must have voted to change vote"
    
    # Check if the vote is actually different
    old_vote = proposal_votes[proposal_id, ctx.caller]
    assert old_vote != new_choice, "New vote must be different from current vote"

    # Update the vote
    proposal_votes[proposal_id, ctx.caller] = new_choice

    # Update tallies if auto-update is enabled
    if auto_update_tallies.get():
        update_current_tallies(proposal_id)


@export
def set_auto_update_tallies(enabled: bool):
    """
    Set whether tallies should automatically update after each vote
    Only owner can change this setting
    """
    assert ctx.caller == owner.get(), "Only owner can change auto update setting"
    assert isinstance(enabled, bool), "Enabled must be a boolean"
    auto_update_tallies.set(enabled)
