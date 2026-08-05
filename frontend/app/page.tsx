export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold">AI Code Review Platform 🚀</h1>

      <p className="mt-4 text-lg">
        Automated GitHub Pull Request Reviews powered by AI
      </p>

      <div className="mt-8 flex gap-4">
        <a
          href="http://localhost:8000/auth/github/login"
          className="px-6 py-3 bg-black text-white rounded-lg"
        >
          Connect GitHub
        </a>

        <button className="px-6 py-3 border rounded-lg">View Reviews</button>
      </div>
    </main>
  );
}
