import unittest
from contracting.stdlib.bridge.time import Datetime
from contracting.stdlib.bridge.decimal import ContractingDecimal
from contracting.client import ContractingClient
import datetime
import os

class TestVotingContract(unittest.TestCase):
    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()
        
        # Setup test data
        self.owner = "contract_owner"
        self.voting_contract_name = "con_voting"
        self.test_voters = ["voter1", "voter2", "voter3"]
        self.test_amounts = [1000, 2000, 3000]  # Increased amounts to cover proposal fees
        
        # Deploy currency contract first
        currency_code = """
currency = Variable()
balances = Hash(default_value=0)
allowances = Hash(default_value=0)

@construct
def seed():
    balances['contract_owner'] = 1_000_000
    balances['dao'] = 0  # Initialize dao account
    currency.set('xian')

@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative amounts!'
    sender = ctx.caller
    assert balances[sender] >= amount, 'Not enough currency to send!'
    balances[sender] -= amount
    balances[to] += amount

@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot approve negative amounts!'
    sender = ctx.caller
    assert balances[sender] >= amount, 'Not enough currency to approve!'
    allowances[sender, to] = amount

@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative amounts!'
    sender = ctx.caller
    assert allowances[main_account, sender] >= amount, 'Not enough allowance to send!'
    assert balances[main_account] >= amount, 'Not enough currency to send!'
    balances[main_account] -= amount
    balances[to] += amount
    allowances[main_account, sender] -= amount

@export
def balance_of(account: str):
    return balances[account]
"""
        # Submit currency contract
        self.client.submit(currency_code, name='currency')
        self.currency = self.client.get_contract('currency')
        
        # Deploy voting contract
        self.contracts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..' ))
        voting_path = os.path.join(self.contracts_dir, "voting.py")
        with open(voting_path) as f:
            code = f.read()
            self.client.submit(code, name=self.voting_contract_name, signer=self.owner)
        
        self.voting = self.client.get_contract(self.voting_contract_name)
        
        # Fund test voters with more tokens
        for voter, amount in zip(self.test_voters, self.test_amounts):
            self.currency.transfer(amount=amount, to=voter, signer=self.owner)

    def approve_proposal_fee(self, voter):
        """Helper method to approve proposal fee for a voter"""
        proposal_fee = self.voting.get_settings()["proposal_fee"]
        self.currency.approve(amount=proposal_fee, to=self.voting_contract_name, signer=voter)

    def create_test_proposal(self, voter, title="Test Proposal Title That Is Long Enough", metadata=None):
        """Helper method to create a test proposal with proper approvals"""
        # Approve fee
        self.approve_proposal_fee(voter)
        
        # Create proposal
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return self.voting.create_proposal(
            title=title,
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            metadata=metadata,
            signer=voter
        )

    def tearDown(self):
        self.client.flush()

    def test_initial_setup(self):
        # GIVEN the initial setup from constructor
        # WHEN checking initial values
        contract_owner = self.voting.owner.get()
        
        
        self.assertEqual(contract_owner, self.owner)

    def test_create_proposal(self):
        # GIVEN a user creating a proposal
        future_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # AND user has approved the fee
        proposal_fee = self.voting.get_settings()["proposal_fee"]
        self.currency.approve(amount=proposal_fee, to=self.voting_contract_name, signer=self.test_voters[0])
        
        # WHEN creating a proposal
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # THEN proposal should be created with correct values and ID should be 0
        self.assertEqual(proposal_id, 0)
        proposal = self.voting.get_proposal(proposal_id=proposal_id)
        self.assertEqual(proposal["title"], "Test Proposal Title That Is Long Enough")
        self.assertEqual(proposal["creator"], self.test_voters[0])
        self.assertEqual(proposal["status"], "active")

        # WHEN creating another proposal
        self.currency.approve(amount=proposal_fee, to=self.voting_contract_name, signer=self.test_voters[0])
        second_proposal_id = self.voting.create_proposal(
            title="Second Test Proposal",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # THEN the second proposal ID should be incremented
        self.assertEqual(second_proposal_id, 1)
        second_proposal = self.voting.get_proposal(proposal_id=second_proposal_id)
        self.assertEqual(second_proposal["title"], "Second Test Proposal")

    def test_vote_on_proposal(self):
        # GIVEN a proposal
        proposal_id = self.create_test_proposal(self.test_voters[0])

        # WHEN voting on the proposal
        self.voting.vote(
            proposal_id=proposal_id,
            choice='y',
            signer=self.test_voters[1]
        )

        # THEN vote should be recorded
        vote_count = self.voting.get_vote_count(proposal_id=proposal_id)
        self.assertEqual(vote_count["for"], 1)
        self.assertEqual(vote_count["against"], 0)
        self.assertEqual(vote_count["abstain"], 0)

    def test_finalize_proposal(self):
        # GIVEN a proposal with votes
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Create proposal with approval
        self.approve_proposal_fee(self.test_voters[0])
        proposal_fee = self.voting.get_settings()["proposal_fee"]  # Get the fee that was paid
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # Add votes from voters with different token amounts
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])  # 1000 - fee tokens
        self.voting.vote(proposal_id=proposal_id, choice='n', signer=self.test_voters[1])  # 2000 tokens
        self.voting.vote(proposal_id=proposal_id, choice='-', signer=self.test_voters[2])  # 3000 tokens

        # WHEN finalizing after expiry
        expired_time = future_time + datetime.timedelta(days=2)
        expired_env = {"now": Datetime(
            expired_time.year,
            expired_time.month,
            expired_time.day,
            expired_time.hour,
            expired_time.minute
        )}

        final_tally = self.voting.finalize_proposal(
            proposal_id=proposal_id,
            signer=self.test_voters[0],
            environment=expired_env
        )

        # THEN votes should be counted correctly and power should match token balances
        self.assertEqual(final_tally["for"], 1)  # 1 vote for
        self.assertEqual(final_tally["against"], 1)  # 1 vote against
        self.assertEqual(final_tally["abstain"], 1)  # 1 abstain
        self.assertEqual(final_tally["pow_for"], 1000 - proposal_fee)  # voter1's tokens minus proposal fee
        self.assertEqual(final_tally["pow_against"], 2000)  # voter2's 2000 tokens
        self.assertEqual(final_tally["pow_abstain"], 3000)  # voter3's 3000 tokens

    def test_cannot_vote_after_expiry(self):
        # GIVEN a proposal
        proposal_id = self.create_test_proposal(self.test_voters[0])

        # WHEN trying to vote after expiry
        expired_time = datetime.datetime.now() + datetime.timedelta(days=2)
        expired_env = {"now": Datetime(
            expired_time.year,
            expired_time.month,
            expired_time.day,
            expired_time.hour,
            expired_time.minute
        )}

        # THEN vote should fail
        with self.assertRaises(AssertionError):
            self.voting.vote(
                proposal_id=proposal_id,
                choice='y',
                signer=self.test_voters[0],
                environment=expired_env
            )

    def test_cannot_vote_twice(self):
        # GIVEN a proposal and a voter who has already voted
        proposal_id = self.create_test_proposal(self.test_voters[0])

        self.voting.vote(
            proposal_id=proposal_id,
            choice='y',
            signer=self.test_voters[0]
        )

        # WHEN trying to vote again with the same choice
        # THEN should raise an exception
        with self.assertRaises(AssertionError) as cm:
            self.voting.vote(
                proposal_id=proposal_id,
                choice='y',  # Same choice as before
                signer=self.test_voters[0]
            )
        self.assertEqual(str(cm.exception), "New vote must be different from current vote")

    def test_invalid_vote_choice(self):
        # GIVEN a proposal
        proposal_id = self.create_test_proposal(self.test_voters[0])

        # WHEN trying to vote with an invalid choice
        # THEN should raise an exception
        with self.assertRaises(AssertionError):
            self.voting.vote(
                proposal_id=proposal_id,
                choice='invalid',
                signer=self.test_voters[0]
            )

    def test_update_current_tallies(self):
        # GIVEN a proposal with votes
        proposal_id = self.create_test_proposal(self.test_voters[0])
        proposal_fee = self.voting.get_settings()["proposal_fee"]

        # Add votes from voters
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])
        
        # WHEN updating current tallies
        current_tally = self.voting.update_current_tallies(proposal_id=proposal_id, signer=self.test_voters[0])
        
        # THEN tallies should be updated
        self.assertEqual(current_tally["for"], 1)
        self.assertEqual(current_tally["against"], 0)
        self.assertEqual(current_tally["abstain"], 0)
        self.assertEqual(current_tally["pow_for"], 1000 - proposal_fee)
        self.assertEqual(current_tally["pow_against"], 0)
        self.assertEqual(current_tally["pow_abstain"], 0)

    def test_title_minimum_length(self):
        # GIVEN a proposal with a short title
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        short_title = "Short"
        
        # WHEN trying to create a proposal
        # THEN it should fail
        with self.assertRaises(AssertionError) as cm:
            self.voting.create_proposal(
                title=short_title,
                description="A" * 100,  # Valid description
                expires_at=expires_at,
                signer=self.test_voters[0]
            )
        self.assertEqual(str(cm.exception), "Title must be at least 10 characters long")

    def test_description_minimum_length(self):
        # GIVEN a proposal with a short description
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        short_description = "Too short description"
        
        # WHEN trying to create a proposal
        # THEN it should fail
        with self.assertRaises(AssertionError) as cm:
            self.voting.create_proposal(
                title="Valid title that is long enough",
                description=short_description,
                expires_at=expires_at,
                signer=self.test_voters[0]
            )
        self.assertEqual(str(cm.exception), "Description must be at least 100 characters long")

    def test_create_proposal_with_valid_lengths(self):
        # GIVEN valid title and description lengths
        valid_title = "This is a valid title"  # 19 characters
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # AND user has approved the fee
        proposal_fee = self.voting.get_settings()["proposal_fee"]
        self.currency.approve(amount=proposal_fee, to=self.voting_contract_name, signer=self.test_voters[0])
        
        # WHEN creating a proposal
        proposal_id = self.voting.create_proposal(
            title=valid_title,
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )
        
        # THEN proposal should be created successfully
        proposal = self.voting.get_proposal(proposal_id=proposal_id)
        self.assertEqual(proposal["title"], valid_title)

    def test_title_must_be_string(self):
        # GIVEN invalid title types
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        invalid_titles = [
            123,  # integer
            ["title"],  # list
            {"title": "title"},  # dict
            None  # None
        ]
        
        # WHEN trying to create proposals with invalid title types
        # THEN they should all fail
        for invalid_title in invalid_titles:
            with self.assertRaises(AssertionError) as cm:
                self.voting.create_proposal(
                    title=invalid_title,
                    description="A" * 100,  # Valid description
                    expires_at=expires_at,
                    signer=self.test_voters[0]
                )
            self.assertEqual(str(cm.exception), "Title must be a string")

    def test_description_must_be_string(self):
        # GIVEN invalid description types
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        invalid_descriptions = [
            123,  # integer
            ["description"],  # list
            {"desc": "description"},  # dict
            None  # None
        ]
        
        # WHEN trying to create proposals with invalid description types
        # THEN they should all fail
        for invalid_description in invalid_descriptions:
            with self.assertRaises(AssertionError) as cm:
                self.voting.create_proposal(
                    title="Valid title that is long enough",
                    description=invalid_description,
                    expires_at=expires_at,
                    signer=self.test_voters[0]
                )
            self.assertEqual(str(cm.exception), "Description must be a string")

    def test_expires_at_must_be_string(self):
        # GIVEN invalid expires_at types
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        invalid_dates = [
            123,  # integer
            ["2023-01-01"],  # list
            {"date": "2023-01-01"},  # dict
            None,  # None
            future_time  # datetime object instead of string
        ]
        
        # WHEN trying to create proposals with invalid expires_at types
        # THEN they should all fail
        for invalid_date in invalid_dates:
            with self.assertRaises(AssertionError) as cm:
                self.voting.create_proposal(
                    title="Valid title that is long enough",
                    description="A" * 100,  # Valid description
                    expires_at=invalid_date,
                    signer=self.test_voters[0]
                )
            self.assertEqual(str(cm.exception), "Expiry date must be a string")

    def test_votes_only_count_with_current_token_balance(self):
        # GIVEN a proposal with votes
        proposal_id = self.create_test_proposal(self.test_voters[0])

        # Add votes from voters
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])  # 1000 tokens
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[1])  # 2000 tokens

        # Transfer all tokens away from voter1 to voter2 (who already has 2000)
        self.currency.transfer(amount=self.currency.balances[self.test_voters[0]], to=self.test_voters[2], signer=self.test_voters[0])

        # WHEN finalizing after expiry
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expired_time = future_time + datetime.timedelta(days=2)
        expired_env = {"now": Datetime(
            expired_time.year,
            expired_time.month,
            expired_time.day,
            expired_time.hour,
            expired_time.minute
        )}

        final_tally = self.voting.finalize_proposal(
            proposal_id=proposal_id,
            signer=self.test_voters[0],
            environment=expired_env
        )

        # THEN only votes from users who still have tokens should be counted
        self.assertEqual(final_tally["for"], 1)  # Only voter2's vote counts
        self.assertEqual(final_tally["against"], 0)
        self.assertEqual(final_tally["abstain"], 0)
        self.assertEqual(final_tally["pow_for"], 2000)  # Only voter2's power counts
        self.assertEqual(final_tally["pow_against"], 0)
        self.assertEqual(final_tally["pow_abstain"], 0)

    def test_can_change_vote_before_expiry(self):
        # GIVEN a proposal with an existing vote
        proposal_id = self.create_test_proposal(self.test_voters[0])
        proposal_fee = self.voting.get_settings()["proposal_fee"]

        # Initial vote
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])
        
        # WHEN changing the vote
        self.voting.vote(proposal_id=proposal_id, choice='n', signer=self.test_voters[0])
        
        # THEN the vote should be updated
        current_tally = self.voting.get_vote_count(proposal_id=proposal_id)
        self.assertEqual(current_tally["for"], 0)
        self.assertEqual(current_tally["against"], 1)
        self.assertEqual(current_tally["pow_for"], 0)
        self.assertEqual(current_tally["pow_against"], 1000 - proposal_fee)

    def test_cannot_change_vote_after_expiry(self):
        # GIVEN a proposal with an existing vote
        proposal_id = self.create_test_proposal(self.test_voters[0])

        # Initial vote
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])
        
        # WHEN trying to change vote after expiry
        expired_time = datetime.datetime.now() + datetime.timedelta(days=2)
        expired_env = {"now": Datetime(
            expired_time.year,
            expired_time.month,
            expired_time.day,
            expired_time.hour,
            expired_time.minute
        )}
        
        # THEN it should fail
        with self.assertRaises(AssertionError):
            self.voting.vote(
                proposal_id=proposal_id,
                choice='n',
                signer=self.test_voters[0],
                environment=expired_env
            )

    def test_cannot_change_to_same_vote(self):
        # GIVEN a proposal with an existing vote
        proposal_id = self.create_test_proposal(self.test_voters[0])

        # Initial vote
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])
        
        # WHEN trying to change to the same vote
        # THEN it should fail
        with self.assertRaises(AssertionError) as cm:
            self.voting.vote(
                proposal_id=proposal_id,
                choice='y',
                signer=self.test_voters[0]
            )
        self.assertEqual(str(cm.exception), "New vote must be different from current vote")

    def test_auto_update_tallies_default_disabled(self):
        # GIVEN a new proposal
        proposal_id = self.create_test_proposal(self.test_voters[0])

        # WHEN voting with auto-update disabled (default)
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])

        # THEN tallies should not be automatically updated
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "total_for"], 0)
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "pow_for"], 0)

    def test_auto_update_tallies_when_enabled(self):
        # GIVEN auto-update is enabled
        self.voting.update_settings(setting_name="auto_update_tallies", value=True, signer=self.owner)
        
        # AND a new proposal
        proposal_id = self.create_test_proposal(self.test_voters[0])
        proposal_fee = self.voting.get_settings()["proposal_fee"]

        # WHEN voting
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])

        # THEN tallies should be automatically updated
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "total_for"], 1)
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "pow_for"], 1000 - proposal_fee)

    def test_auto_update_on_vote_change(self):
        # GIVEN auto-update is enabled
        self.voting.update_settings(setting_name="auto_update_tallies", value=1, signer=self.owner)
        
        # AND a proposal with an existing vote
        proposal_id = self.create_test_proposal(self.test_voters[0])
        proposal_fee = self.voting.get_settings()["proposal_fee"]

        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])
        
        # WHEN changing vote
        self.voting.vote(proposal_id=proposal_id, choice='n', signer=self.test_voters[0])

        # THEN tallies should be automatically updated
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "total_for"], 0)
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "total_against"], 1)
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "pow_for"], 0)
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "pow_against"], 1000 - proposal_fee)

    def test_only_owner_can_update_settings(self):
        # WHEN non-owner tries to change settings
        # THEN it should fail
        with self.assertRaises(AssertionError) as cm:
            self.voting.update_settings(
                setting_name="auto_update_tallies",
                value=1,
                signer=self.test_voters[0]
            )
        self.assertEqual(str(cm.exception), "Only owner can change settings")

    def test_update_title_length_limits(self):
        # WHEN owner updates title length limits
        self.voting.update_settings(
            setting_name="title_length_limits",
            value=[15, 60],
            signer=self.owner
        )
        
        # THEN settings should be updated
        settings = self.voting.get_settings()
        self.assertEqual(settings["min_title_length"], 15)
        self.assertEqual(settings["max_title_length"], 60)

    def test_update_proposal_fee(self):
        # WHEN owner updates proposal fee
        self.voting.update_settings(
            setting_name="proposal_fee",
            value=200,
            signer=self.owner
        )
        
        # THEN fee should be updated
        settings = self.voting.get_settings()
        self.assertEqual(settings["proposal_fee"], 200)

    def test_create_proposal_with_fee(self):
        # GIVEN a proposal fee is set
        proposal_fee = 50
        self.voting.update_settings(setting_name="proposal_fee", value=proposal_fee, signer=self.owner)
        
        # AND a future expiry date
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # AND user has approved the fee
        self.currency.approve(amount=proposal_fee, to=self.voting_contract_name, signer=self.test_voters[0])
        
        # Record initial balances
        initial_creator_balance = self.currency.balances[self.test_voters[0]]
        initial_dao_balance = self.currency.balances['dao']
        
        # WHEN creating a proposal
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )
        
        # THEN fee should be deducted from creator's balance
        final_creator_balance = self.currency.balances[self.test_voters[0]]
        self.assertEqual(final_creator_balance, initial_creator_balance - proposal_fee)
        
        # AND fee should be added to dao's balance
        final_dao_balance = self.currency.balances['dao']
        self.assertEqual(final_dao_balance, initial_dao_balance + proposal_fee)
        
        # AND proposal should store fee paid
        proposal = self.voting.get_proposal(proposal_id=proposal_id)
        self.assertEqual(proposal["fee_paid"], proposal_fee)

    def test_create_proposal_without_allowance(self):
        # GIVEN a proposal fee is set
        proposal_fee = 50
        self.voting.update_settings(setting_name="proposal_fee", value=proposal_fee, signer=self.owner)
        
        # WHEN trying to create a proposal without approving the fee
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # THEN it should fail
        with self.assertRaises(AssertionError) as cm:
            self.voting.create_proposal(
                title="Test Proposal Title That Is Long Enough",
                description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                           " Adding more context and information to ensure it's comprehensive.",
                expires_at=expires_at,
                signer=self.test_voters[0]
            )
        self.assertTrue("Not enough allowance to send" in str(cm.exception))

    def test_create_proposal_with_insufficient_balance_for_fee(self):
        # GIVEN a proposal fee higher than user's balance
        current_balance = self.currency.balances[self.test_voters[0]]
        high_fee = current_balance + 1
        self.voting.update_settings(setting_name="proposal_fee", value=high_fee, signer=self.owner)
        
        # WHEN trying to approve more than balance
        # THEN it should fail
        with self.assertRaises(AssertionError) as cm:
            self.currency.approve(amount=high_fee, to=self.voting_contract_name, signer=self.test_voters[0])
        self.assertTrue("Not enough currency to approve" in str(cm.exception))

    def test_title_length_limits(self):
        # GIVEN custom title length limits
        self.voting.update_settings(setting_name="title_length_limits", value=[15, 30], signer=self.owner)
        
        # WHEN trying to create a proposal with too short title
        with self.assertRaises(AssertionError) as cm:
            self.create_test_proposal(self.test_voters[0], title="Too Short")
        self.assertTrue("Title must be at least 15 characters" in str(cm.exception))
        
        # AND when trying with too long title
        with self.assertRaises(AssertionError) as cm:
            self.create_test_proposal(
                self.test_voters[0],
                title="This title is way too long for the maximum limit"
            )
        self.assertTrue("Title must be at most 30 characters" in str(cm.exception))
        
        # THEN should succeed with valid title length
        valid_title = "This is a valid title"  # 19 characters
        proposal_id = self.create_test_proposal(self.test_voters[0], title=valid_title)
        
        proposal = self.voting.get_proposal(proposal_id=proposal_id)
        self.assertEqual(proposal["title"], valid_title)

    def test_invalid_setting_name(self):
        # WHEN trying to update an invalid setting
        # THEN it should fail
        with self.assertRaises(Exception) as cm:
            self.voting.update_settings(
                setting_name="invalid_setting",
                value=True,
                signer=self.owner
            )
        self.assertEqual(str(cm.exception), "Invalid setting name")

    def test_invalid_setting_value_type(self):
        # WHEN trying to update settings with invalid value types
        # THEN it should fail
        with self.assertRaises(AssertionError):
            self.voting.update_settings(
                setting_name="auto_update_tallies",
                value="not_an_integer",
                signer=self.owner
            )
        
        with self.assertRaises(AssertionError):
            self.voting.update_settings(
                setting_name="proposal_fee",
                value="not_an_integer",
                signer=self.owner
            )
        
        with self.assertRaises(AssertionError):
            self.voting.update_settings(
                setting_name="title_length_limits",
                value=15,  # Should be a list
                signer=self.owner
            )

    def test_create_proposal_with_metadata(self):
        # GIVEN metadata with different value types
        metadata = {
            "category": "governance",
            "priority": 1,
            "urgent": True,
            "impact_score": 4.5
        }

        # WHEN creating a proposal with metadata
        proposal_id = self.create_test_proposal(self.test_voters[0], metadata=metadata)

        # THEN proposal should be created with the metadata
        proposal = self.voting.get_proposal(proposal_id=proposal_id)
        stored_metadata = proposal["metadata"]
        
        # Verify each key-value pair matches
        for key, value in metadata.items():
            self.assertEqual(stored_metadata[key], value)

    def test_create_proposal_with_invalid_metadata(self):
        # GIVEN invalid metadata types
        invalid_metadata_cases = [
            # Invalid key type
            {1: "value"},
            # Invalid value types
            {"key": [1, 2, 3]},  # List not allowed
            {"key": {"nested": "dict"}},  # Dict not allowed
            {"key": None},  # None not allowed
            {"key": lambda x: x},  # Function not allowed
            {"key": object()},  # Object not allowed
        ]

        # WHEN trying to create proposals with invalid metadata
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")

        for invalid_metadata in invalid_metadata_cases:
            # THEN it should fail with assertion error about metadata types
            with self.assertRaises(AssertionError) as cm:
                self.approve_proposal_fee(self.test_voters[0])
                self.voting.create_proposal(
                    title="Test Proposal Title That Is Long Enough",
                    description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                              " Adding more context and information to ensure it's comprehensive.",
                    expires_at=expires_at,
                    metadata=invalid_metadata,
                    signer=self.test_voters[0]
                )
                self.assertTrue("Metadata values must be primitive types" in str(cm.exception) or 
                              "Metadata keys must be strings" in str(cm.exception))

    def test_create_proposal_with_empty_metadata(self):
        # WHEN creating a proposal with no metadata
        proposal_id = self.create_test_proposal(self.test_voters[0])

        # THEN proposal should be created with empty metadata dict
        proposal = self.voting.get_proposal(proposal_id=proposal_id)
        self.assertEqual(proposal["metadata"], {})

    def test_create_proposal_with_none_metadata(self):
        # WHEN creating a proposal with None metadata
        proposal_id = self.create_test_proposal(self.test_voters[0], metadata=None)

        # THEN proposal should be created with empty metadata dict
        proposal = self.voting.get_proposal(proposal_id=proposal_id)
        self.assertEqual(proposal["metadata"], {})

    def test_finalize_proposal_event_types(self):
        # GIVEN a proposal with votes
        self.currency.balances[self.test_voters[0]] = 1000.1
        proposal_id = self.create_test_proposal(self.test_voters[0])
        proposal_fee = self.voting.get_settings()["proposal_fee"]

        # Add votes from voters with different token amounts
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])  # 1000 - fee tokens
        self.voting.vote(proposal_id=proposal_id, choice='n', signer=self.test_voters[1])  # 2000 tokens
        self.voting.vote(proposal_id=proposal_id, choice='-', signer=self.test_voters[2])  # 3000 tokens

        # WHEN finalizing after expiry
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expired_time = future_time + datetime.timedelta(days=2)
        expired_env = {"now": Datetime(
            expired_time.year,
            expired_time.month,
            expired_time.day,
            expired_time.hour,
            expired_time.minute
        )}

        # Print the types of values before finalization for debugging
        current_tally = self.voting.get_vote_count(proposal_id=proposal_id)
        print("Vote count types:")
        print(f"pow_for type: {type(current_tally['pow_for'])}")
        print(f"pow_against type: {type(current_tally['pow_against'])}")
        print(f"pow_abstain type: {type(current_tally['pow_abstain'])}")
        breakpoint()
        # THEN finalization should succeed without type errors
        final_tally = self.voting.finalize_proposal(
            proposal_id=proposal_id,
            signer=self.test_voters[0],
            environment=expired_env
        )

        # Verify the types of the returned values
        self.assertIsInstance(final_tally["pow_for"], (int, float, ContractingDecimal))
        self.assertIsInstance(final_tally["pow_against"], (int, float, ContractingDecimal))
        self.assertIsInstance(final_tally["pow_abstain"], (int, float, ContractingDecimal))

        # Verify the values are as expected
        self.assertEqual(final_tally["pow_for"], 1000.1 - proposal_fee)
        self.assertEqual(final_tally["pow_against"], 2000)
        self.assertEqual(final_tally["pow_abstain"], 3000)