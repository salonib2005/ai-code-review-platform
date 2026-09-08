"use client";

import { useEffect, useState } from "react";

export default function Dashboard() {
  const [user, setUser] = useState<any>(null);
  const [repositories, setRepositories] = useState<any[]>([]);

  const [reviewResult, setReviewResult] = useState<any>(null);
  const [reviewHistory, setReviewHistory] = useState<any[]>([]);
  const [selectedReview, setSelectedReview] = useState<any>(null);

  const [loading, setLoading] = useState(true);
  const [reviewLoading, setReviewLoading] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const username = "salonib2005";

        // USER

        const userResponse = await fetch(
          "http://localhost:8000/users/" + username,
        );

        const userData = await userResponse.json();

        console.log("USER:", userData);

        setUser(userData);

        // REPOSITORIES

        const repoResponse = await fetch(
          "http://localhost:8000/repositories/" + userData.id,
        );

        const repoData = await repoResponse.json();

        console.log("REPOSITORIES:", repoData);

        setRepositories(repoData);

        // HISTORY

        const historyResponse = await fetch(
          "http://localhost:8000/history/" + userData.id,
        );

        const historyData = await historyResponse.json();

        console.log("HISTORY:", historyData);

        setReviewHistory(historyData);
      } catch (error) {
        console.error("ERROR:", error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  async function reviewCode(repoUrl: string) {
    try {
      setReviewLoading(true);

      const response = await fetch("http://localhost:8000/review/review/", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          repo_url: repoUrl,
        }),
      });

      const data = await response.json();

      console.log("REVIEW RESULT:", data);
      console.log("REVIEW ISSUES:", data.issues);

      setReviewResult(data);

      // Refresh history

      if (user) {
        const historyResponse = await fetch(
          "http://localhost:8000/history/" + user.id,
        );

        const historyData = await historyResponse.json();

        setReviewHistory(historyData);
      }
    } catch (error) {
      console.error("Review Error:", error);
    } finally {
      setReviewLoading(false);
    }
  }

  async function openReview(reviewId: number) {
    try {
      const response = await fetch(
        "http://localhost:8000/history/review/" + reviewId,
      );

      const data = await response.json();

      console.log("OLD REVIEW:", data);

      setSelectedReview(data);

      setTimeout(() => {
        document.getElementById("review-details")?.scrollIntoView({
          behavior: "smooth",
        });
      }, 100);
    } catch (error) {
      console.error("History Error:", error);
    }
  }

  if (loading) {
    return <div className="p-10 text-xl">Loading Dashboard...</div>;
  }

  return (
    <main className="p-10">
      {/* PROFILE */}

      {user && (
        <div
          className="
          bg-white
          rounded-2xl
          shadow
          p-6
          flex
          items-center
          gap-6
          mb-10
        "
        >
          <img
            src={user.avatar}
            alt="profile"
            className="
              w-24
              h-24
              rounded-full
              border
            "
          />

          <div>
            <h1 className="text-3xl font-bold">Welcome {user.name} 👋</h1>

            <p className="text-gray-500 mt-2">@{user.username}</p>

            <p className="text-gray-400 text-sm">GitHub Developer</p>
          </div>
        </div>
      )}

      {/* REPOSITORIES */}

      <h2 className="text-3xl font-bold mb-2">Your GitHub Repositories 🚀</h2>

      <p className="text-gray-500 mb-6">
        Analyze repositories using AI code review
      </p>

      <div className="grid gap-6">
        {repositories.map((repo: any) => (
          <div
            key={repo.id}
            className="
              bg-white
              rounded-2xl
              shadow
              border
              p-6
              hover:shadow-xl
              transition
            "
          >
            <h3 className="text-xl font-bold">📁 {repo.name}</h3>

            <p className="mt-3 text-gray-600">
              🐍 Language: {repo.language || "Not specified"}
            </p>

            <div className="flex gap-4 mt-5">
              <a
                href={repo.url}
                target="_blank"
                rel="noopener noreferrer"
                className="
                  px-5
                  py-2
                  border
                  rounded-lg
                  hover:bg-gray-100
                "
              >
                Open Repository
              </a>

              <button
                onClick={() => reviewCode(repo.url)}
                disabled={reviewLoading}
                className="
                  px-5
                  py-2
                  bg-black
                  text-white
                  rounded-lg
                  hover:bg-gray-700
                  disabled:opacity-50
                "
              >
                {reviewLoading ? "🤖 Reviewing..." : "🚀 Review Code"}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* CURRENT REVIEW */}

      {reviewResult && (
        <div className="mt-12">
          <h2 className="text-3xl font-bold mb-6">AI Review Results 🤖</h2>

          <div className="grid gap-5">
            {reviewResult.issues.map((issue: any, index: number) => (
              <div
                key={index}
                className={`
                  rounded-2xl
                  border
                  p-6
                  ${
                    issue.severity === "warning"
                      ? "bg-yellow-50 border-yellow-300"
                      : "bg-blue-50 border-blue-300"
                  }
                `}
              >
                <h3 className="text-xl font-bold">
                  {issue.severity === "warning"
                    ? "⚠️ Warning"
                    : "💡 Suggestion"}
                </h3>

                <p className="mt-3 font-semibold">File: {issue.file}</p>

                <p>Line: {issue.line}</p>

                <p className="mt-3">{issue.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* HISTORY */}

      {reviewHistory.length > 0 && (
        <div className="mt-12">
          <h2 className="text-3xl font-bold mb-6">Previous Reviews 📜</h2>

          <div className="grid gap-5">
            {reviewHistory.map((review: any) => (
              <div
                key={review.id}
                className="
                  bg-white
                  border
                  rounded-2xl
                  shadow
                  p-6
                  hover:shadow-xl
                  transition
                "
              >
                <h3
                  onClick={() => openReview(review.id)}
                  className="
                    text-xl
                    font-bold
                    cursor-pointer
                    hover:text-blue-600
                  "
                >
                  🚀 AI Code Review #{review.id}
                </h3>

                <p className="mt-3 text-gray-600">Repository:</p>

                <a
                  href={review.repo_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="
                    text-blue-600
                    underline
                  "
                >
                  🔗 {review.repo_url}
                </a>

                <div className="mt-4 space-y-2">
                  <p>
                    🐛 Issues Found:
                    <b> {review.issues_count}</b>
                  </p>

                  <p className="text-yellow-600">
                    ⚠️ Warnings:
                    <b> {review.warnings}</b>
                  </p>

                  <p className="text-blue-600">
                    💡 Suggestions:
                    <b> {review.suggestions}</b>
                  </p>

                  <p className="text-gray-500">
                    📅 {new Date(review.created_at).toLocaleString()}
                  </p>
                </div>

                <p
                  onClick={() => openReview(review.id)}
                  className="
                    mt-4
                    text-sm
                    text-gray-400
                    cursor-pointer
                    hover:text-blue-500
                  "
                >
                  Click to view review details →
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SELECTED REVIEW DETAILS */}

      {selectedReview && (
        <div id="review-details" className="mt-12">
          <h2 className="text-3xl font-bold mb-6">
            Previous Review Details 🤖
          </h2>

          <div className="grid gap-5">
            {selectedReview.issues.map((issue: any, index: number) => (
              <div
                key={index}
                className={`
                  rounded-2xl
                  border
                  p-6
                  ${
                    issue.severity === "warning"
                      ? "bg-yellow-50 border-yellow-300"
                      : "bg-blue-50 border-blue-300"
                  }
                `}
              >
                <h3 className="text-xl font-bold">
                  {issue.severity === "warning"
                    ? "⚠️ Warning"
                    : "💡 Suggestion"}
                </h3>

                <p className="mt-3 font-semibold">File: {issue.file}</p>

                <p>Line: {issue.line}</p>

                <p className="mt-3">{issue.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}

//hi this is saloni wat up
