/**
 * DreamCo Control Tower — Repo Manager
 *
 * Provides GitHub API helpers for repository monitoring:
 *   - Fetch open PRs, last commit, and workflow runs
 *   - Register new repos in the bot registry
 *   - Detect conflicts and workflow failures
 */

import { fileURLToPath } from "url";
import { dirname } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));

// ---------------------------------------------------------------------------
// GitHub helpers (uses fetch — available in Node >=18)
// ---------------------------------------------------------------------------

/**
 * Return a GitHub REST API response.
 * @param {string} path  - API path e.g. "/repos/owner/repo/pulls"
 * @param {string} [token] - Optional bearer token
 */
async function ghFetch(path, token) {
  const headers = {
    Accept: "application/vnd.github+json",
    "User-Agent": "DreamCo-Control-Tower/1.0",
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const resp = await fetch(`https://api.github.com${path}`, { headers });
  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(`GitHub API ${resp.status}: ${text.slice(0, 200)}`);
  }
  return resp.json();
}

// ---------------------------------------------------------------------------
// Repo status
// ---------------------------------------------------------------------------

/**
 * Fetch a comprehensive status summary for a GitHub repository.
 *
 * @param {string} owner     - GitHub username or org
 * @param {string} repoName  - Repository name
 * @returns {Promise<object>}
 */
export async function getRepoStatus(owner, repoName) {
  const token = process.env.GITHUB_TOKEN;

  try {
    const [prs, commits, runsData] = await Promise.all([
      ghFetch(`/repos/${owner}/${repoName}/pulls?state=open&per_page=10`, token),
      ghFetch(`/repos/${owner}/${repoName}/commits?per_page=1`, token),
      ghFetch(`/repos/${owner}/${repoName}/actions/runs?per_page=1`, token),
    ]);

    const lastCommit = commits[0] ?? {};
    const lastRun = runsData.workflow_runs?.[0] ?? {};

    return {
      repo: repoName,
      owner,
      online: true,
      openPRs: prs.length,
      lastCommitSha: lastCommit.sha?.slice(0, 7) ?? "",
      lastCommitMessage: lastCommit.commit?.message?.split("\n")[0]?.slice(0, 80) ?? "",
      lastCommitAt: lastCommit.commit?.committer?.date ?? "",
      lastWorkflowName: lastRun.name ?? "",
      lastWorkflowStatus: lastRun.conclusion ?? "unknown",
      conflictAlert: lastRun.conclusion === "failure",
      highPRAlert: prs.length > 3,
      timestamp: new Date().toISOString(),
    };
  } catch (err) {
    return {
      repo: repoName,
      owner,
      online: false,
      error: err.message,
      openPRs: 0,
      lastCommitSha: "",
      lastCommitMessage: "",
      lastCommitAt: "",
      lastWorkflowName: "",
      lastWorkflowStatus: "unknown",
      conflictAlert: false,
      highPRAlert: false,
      timestamp: new Date().toISOString(),
    };
  }
}

/**
 * Fetch status for multiple repositories in parallel.
 * @param {string} owner
 * @param {string[]} repoNames
 * @returns {Promise<object[]>}
 */
export async function getMultiRepoStatus(owner, repoNames) {
  return Promise.all(repoNames.map((r) => getRepoStatus(owner, r)));
}

// ---------------------------------------------------------------------------
// Conflict detection
// ---------------------------------------------------------------------------

/**
 * Return repos that have workflow failures or many open PRs.
 * @param {object[]} repoStatuses - Array of repo status objects
 * @returns {object[]} Filtered list of repos with detected issues
 */
export function detectConflicts(repoStatuses) {
  return repoStatuses.filter((r) => r.conflictAlert || r.highPRAlert);
}

// ---------------------------------------------------------------------------
// Default export
// ---------------------------------------------------------------------------

export default {
  getRepoStatus,
  getMultiRepoStatus,
  detectConflicts,
};
