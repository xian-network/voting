import { useState, useEffect } from 'react';

const HomePage: React.FC = () => {
  // Proposal state
  const [proposals, setProposals] = useState<{ id: number; title: string; description: string }[]>([
    { id: 1, title: 'Improve UI', description: 'Update the interface with vibrant vaporwave style and smooth animations.' },
    { id: 2, title: 'Refine Voting Power', description: 'Optimize token-based weighted voting for balanced outcomes.' }
  ]);
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [showForm, setShowForm] = useState(false);

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newDescription.trim()) return;
    const newProposal = { id: proposals.length + 1, title: newTitle, description: newDescription };
    setProposals([newProposal, ...proposals]);
    setNewTitle('');
    setNewDescription('');
    setShowForm(false);
  };

  // Alert state for life fact messages
  const facts = [
    "Life is a beautiful journey.",
    "Every moment counts.",
    "Believe in yourself.",
    "Happiness comes from within.",
    "Embrace change and grow."
  ];
  const [alertMessage, setAlertMessage] = useState<string>('');
  const [showAlert, setShowAlert] = useState<boolean>(false);

  useEffect(() => {
    const showFactAlert = () => {
      const fact = facts[Math.floor(Math.random() * facts.length)];
      setAlertMessage(fact);
      setShowAlert(true);
      setTimeout(() => {
        setShowAlert(false);
      }, 5000);
    };

    const initialTimeout = setTimeout(() => {
      showFactAlert();
    }, 2000);
    const intervalId = setInterval(() => {
      showFactAlert();
    }, 15000);
    return () => {
      clearInterval(intervalId);
      clearTimeout(initialTimeout);
    };
  }, []);

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-purple-500 to-pink-500 overflow-hidden">
      {/* Audio element playing classical midi jazz */}
      <audio autoPlay loop>
        <source src="/classical-jazz.mid" type="audio/midi" />
        Your browser does not support the audio element.
      </audio>

      {/* Animated Cloud Background */}
      <div className="absolute inset-0">
        <div className="absolute top-10 left-0 w-16 h-16 bg-white rounded-full opacity-70 animate-cloud1" />
        <div className="absolute top-20 left-0 w-20 h-20 bg-white rounded-full opacity-70 animate-cloud2" />
        <div className="absolute top-32 left-0 w-12 h-12 bg-white rounded-full opacity-70 animate-cloud3" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 py-10 px-4">
        <header className="text-center mb-10">
          <h1 className="text-5xl font-extrabold text-white mb-4 animate-pulse">Contributor Voting System</h1>
          <p className="text-xl text-white mb-6">Decentralized voting for token holders. Create proposals and vote in real-time.</p>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-white text-pink-500 font-bold px-6 py-2 rounded-full hover:bg-pink-500 hover:text-white transition"
          >
            {showForm ? 'Cancel' : 'New Proposal'}
          </button>
        </header>

        {showForm && (
          <div className="max-w-xl mx-auto mb-8 bg-white bg-opacity-20 p-6 rounded-lg shadow-lg">
            <form onSubmit={handleFormSubmit}>
              <div className="mb-4">
                <label className="block text-white text-lg font-semibold mb-2">Title</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="Enter proposal title"
                  className="w-full px-4 py-2 rounded-md bg-white bg-opacity-80 border border-gray-300"
                />
              </div>
              <div className="mb-4">
                <label className="block text-white text-lg font-semibold mb-2">Description</label>
                <textarea
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Enter proposal description"
                  className="w-full px-4 py-2 rounded-md bg-white bg-opacity-80 border border-gray-300"
                />
              </div>
              <button type="submit" className="bg-pink-500 text-white font-bold px-6 py-2 rounded-full hover:bg-pink-600 transition">
                Submit Proposal
              </button>
            </form>
          </div>
        )}

        <section>
          <h2 className="text-3xl font-bold text-white text-center mb-6">Active Proposals</h2>
          <div className="max-w-2xl mx-auto">
            {proposals.map((proposal) => (
              <div
                key={proposal.id}
                className="cursor-pointer p-4 mb-4 bg-white bg-opacity-20 border border-white/30 rounded-lg shadow-lg transition-transform transform hover:scale-105"
              >
                <h3 className="text-2xl font-bold text-white">{proposal.title}</h3>
                <p className="mt-2 text-white">{proposal.description}</p>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Alert Component for Life Facts */}
      <div
        className={`fixed bottom-10 left-1/2 transform -translate-x-1/2 bg-white bg-opacity-70 text-pink-700 font-semibold px-6 py-3 rounded-full shadow-lg transition-opacity duration-1000 ${showAlert ? 'opacity-100' : 'opacity-0'}`}
      >
        {alertMessage}
      </div>

      <style jsx>{`
        @keyframes cloudAnimation {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(110vw); }
        }
        .animate-cloud1 {
          animation: cloudAnimation 30s linear infinite;
        }
        .animate-cloud2 {
          animation: cloudAnimation 35s linear infinite;
          animation-delay: 5s;
        }
        .animate-cloud3 {
          animation: cloudAnimation 40s linear infinite;
          animation-delay: 10s;
        }
      `}</style>
    </div>
  );
};

export default HomePage;