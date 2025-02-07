import unittest
from contracting.stdlib.bridge.time import Datetime
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
        self.test_amounts = [100, 200, 300]
        
        # Deploy currency contract first
        currency_code = """
currency = Variable()
balances = Hash(default_value=0)

@construct
def seed():
    balances['contract_owner'] = 1_000_000
    currency.set('xian')

@export
def transfer(amount: float, to: str):
    sender = ctx.caller
    assert balances[sender] >= amount, 'Not enough currency to send!'
    balances[sender] -= amount
    balances[to] += amount

@export
def balance_of(account: str):
    return balances[account]
"""
        # Submit and call seed() for currency contract
        self.client.submit(currency_code, name='currency')
        currency = self.client.get_contract('currency')
        
        # Deploy voting contract
        self.contracts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..' ))
        voting_path = os.path.join(self.contracts_dir, "voting.py")
        with open(voting_path) as f:
            code = f.read()
            self.client.submit(code, name=self.voting_contract_name, signer=self.owner)
        
        self.voting = self.client.get_contract(self.voting_contract_name)
        self.currency = self.client.get_contract("currency")
        
        # Fund test voters
        for voter, amount in zip(self.test_voters, self.test_amounts):
            self.currency.transfer(amount=amount, to=voter, signer=self.owner)

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
        
        # WHEN creating a proposal
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # THEN proposal should be created with correct values
        proposal = self.voting.get_proposal(proposal_id=proposal_id)
        self.assertEqual(proposal["title"], "Test Proposal Title That Is Long Enough")
        self.assertEqual(proposal["creator"], self.test_voters[0])
        self.assertEqual(proposal["status"], "active")

    def test_vote_on_proposal(self):
        # GIVEN a proposal
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # WHEN voting on the proposal
        self.voting.vote(
            proposal_id=proposal_id,
            choice='y',
            signer=self.test_voters[0]
        )

        # THEN vote should be recorded (but not weighted yet)
        vote_count = self.voting.get_vote_count(proposal_id=proposal_id)
        self.assertEqual(vote_count["for"], 1)
        self.assertEqual(vote_count["against"], 0)
        self.assertEqual(vote_count["abstain"], 0)

    def test_finalize_proposal(self):
        # GIVEN a proposal with votes
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # Add some votes from voters with different token amounts
        # voter1: 100 tokens votes yes
        # voter2: 200 tokens votes no
        # voter3: 300 tokens abstains
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])
        self.voting.vote(proposal_id=proposal_id, choice='n', signer=self.test_voters[1])
        self.voting.vote(proposal_id=proposal_id, choice='-', signer=self.test_voters[2])

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
        self.assertEqual(final_tally["pow_for"], 100)  # voter1's 100 tokens
        self.assertEqual(final_tally["pow_against"], 200)  # voter2's 200 tokens
        self.assertEqual(final_tally["pow_abstain"], 300)  # voter3's 300 tokens

    def test_cannot_vote_after_expiry(self):
        # GIVEN a proposal
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # WHEN trying to vote after expiry
        expired_time = future_time + datetime.timedelta(days=2)
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
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        self.voting.vote(
            proposal_id=proposal_id,
            choice='y',
            signer=self.test_voters[0]
        )

        # WHEN trying to vote again
        # THEN should raise an exception
        with self.assertRaises(AssertionError):
            self.voting.vote(
                proposal_id=proposal_id,
                choice='n',
                signer=self.test_voters[0]
            )

    def test_invalid_vote_choice(self):
        # GIVEN a proposal
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

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
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # Add votes from voters with different token amounts
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])  # 100 tokens
        self.voting.vote(proposal_id=proposal_id, choice='n', signer=self.test_voters[1])  # 200 tokens
        
        # WHEN updating current tallies
        current_tally = self.voting.update_current_tallies(proposal_id=proposal_id, signer=self.test_voters[0])
        
        # THEN tallies should be updated in the proposal_metrics hash
        self.assertEqual(current_tally["for"], 1)
        self.assertEqual(current_tally["against"], 1)
        self.assertEqual(current_tally["abstain"], 0)
        self.assertEqual(current_tally["pow_for"], 100)
        self.assertEqual(current_tally["pow_against"], 200)
        self.assertEqual(current_tally["pow_abstain"], 0)
        
        # And stored values should match
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "total_for"], 1)
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "pow_for"], 100)

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
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        valid_title = "This is a valid title for a proposal"
        valid_description = "This is a valid description that is definitely long enough. " * 3  # Multiplied to ensure > 100 chars
        
        # WHEN creating a proposal
        proposal_id = self.voting.create_proposal(
            title=valid_title,
            description=valid_description,
            expires_at=expires_at,
            signer=self.test_voters[0]
        )
        
        # THEN proposal should be created successfully
        proposal = self.voting.get_proposal(proposal_id=proposal_id)
        self.assertEqual(proposal["title"], valid_title)
        self.assertEqual(proposal["description"], valid_description)

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
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # Add votes from voters
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])  # 100 tokens
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[1])  # 200 tokens

        # Transfer all tokens away from voter1
        self.currency.transfer(amount=100, to=self.test_voters[2], signer=self.test_voters[0])

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

        # THEN only votes from users who still have tokens should be counted
        self.assertEqual(final_tally["for"], 1)  # Only voter2's vote counts
        self.assertEqual(final_tally["against"], 0)
        self.assertEqual(final_tally["abstain"], 0)
        self.assertEqual(final_tally["pow_for"], 200)  # Only voter2's power counts
        self.assertEqual(final_tally["pow_against"], 0)
        self.assertEqual(final_tally["pow_abstain"], 0)

    def test_can_change_vote_before_expiry(self):
        # GIVEN a proposal with an existing vote
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # Initial vote
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])
        
        # WHEN changing the vote
        self.voting.change_vote(proposal_id=proposal_id, new_choice='n', signer=self.test_voters[0])
        
        # THEN the vote should be updated
        current_tally = self.voting.get_vote_count(proposal_id=proposal_id)
        self.assertEqual(current_tally["for"], 0)
        self.assertEqual(current_tally["against"], 1)
        self.assertEqual(current_tally["pow_for"], 0)
        self.assertEqual(current_tally["pow_against"], 100)  # voter0's 100 tokens

    def test_cannot_change_vote_after_expiry(self):
        # GIVEN a proposal with an existing vote
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # Initial vote
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])
        
        # WHEN trying to change vote after expiry
        expired_time = future_time + datetime.timedelta(days=2)
        expired_env = {"now": Datetime(
            expired_time.year,
            expired_time.month,
            expired_time.day,
            expired_time.hour,
            expired_time.minute
        )}
        
        # THEN it should fail
        with self.assertRaises(AssertionError):
            self.voting.change_vote(
                proposal_id=proposal_id,
                new_choice='n',
                signer=self.test_voters[0],
                environment=expired_env
            )

    def test_cannot_change_to_same_vote(self):
        # GIVEN a proposal with an existing vote
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # Initial vote
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])
        
        # WHEN trying to change to the same vote
        # THEN it should fail
        with self.assertRaises(AssertionError) as cm:
            self.voting.change_vote(
                proposal_id=proposal_id,
                new_choice='y',
                signer=self.test_voters[0]
            )
        self.assertEqual(str(cm.exception), "New vote must be different from current vote")

    def test_must_have_voted_to_change_vote(self):
        # GIVEN a proposal
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # WHEN trying to change vote without having voted
        # THEN it should fail
        with self.assertRaises(AssertionError) as cm:
            self.voting.change_vote(
                proposal_id=proposal_id,
                new_choice='y',
                signer=self.test_voters[0]
            )
        self.assertEqual(str(cm.exception), "Must have voted to change vote")

    def test_auto_update_tallies_default_disabled(self):
        # GIVEN a new proposal
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # WHEN voting with auto-update disabled (default)
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])

        # THEN tallies should not be automatically updated
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "total_for"], 0)
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "pow_for"], 0)

    def test_auto_update_tallies_when_enabled(self):
        # GIVEN auto-update is enabled
        self.voting.set_auto_update_tallies(enabled=True, signer=self.owner)
        
        # AND a new proposal
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        # WHEN voting
        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])

        # THEN tallies should be automatically updated
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "total_for"], 1)
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "pow_for"], 100)  # voter0's 100 tokens

    def test_auto_update_on_vote_change(self):
        # GIVEN auto-update is enabled
        self.voting.set_auto_update_tallies(enabled=True, signer=self.owner)
        
        # AND a proposal with an existing vote
        future_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = future_time.strftime("%Y-%m-%d %H:%M:%S")
        
        proposal_id = self.voting.create_proposal(
            title="Test Proposal Title That Is Long Enough",
            description="This is a very detailed description that meets the minimum length requirement. It contains specific details about what the proposal aims to achieve." + 
                       " Adding more context and information to ensure it's comprehensive.",
            expires_at=expires_at,
            signer=self.test_voters[0]
        )

        self.voting.vote(proposal_id=proposal_id, choice='y', signer=self.test_voters[0])
        
        # WHEN changing vote
        self.voting.change_vote(proposal_id=proposal_id, new_choice='n', signer=self.test_voters[0])

        # THEN tallies should be automatically updated
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "total_for"], 0)
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "total_against"], 1)
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "pow_for"], 0)
        self.assertEqual(self.voting.proposal_metrics[proposal_id, "pow_against"], 100)

    def test_only_owner_can_set_auto_update(self):
        # WHEN non-owner tries to change auto-update setting
        # THEN it should fail
        with self.assertRaises(AssertionError) as cm:
            self.voting.set_auto_update_tallies(
                enabled=True,
                signer=self.test_voters[0]
            )
        self.assertEqual(str(cm.exception), "Only owner can change auto update setting") 