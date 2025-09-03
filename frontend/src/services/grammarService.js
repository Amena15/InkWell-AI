import axios from 'axios';

const API_BASE_URL = 'http://localhost:8004/api/v1';

/**
 * Check grammar and style in the provided text
 * @param {string} text - The text to check
 * @returns {Promise<Object>} - Grammar check results
 */
export const checkGrammar = async (text) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/document/check-grammar`,
      { text }
    );
    return response.data;
  } catch (error) {
    console.error('Error checking grammar:', error);
    throw error;
  }
};

/**
 * Get a user-friendly message for a grammar issue
 * @param {Object} issue - The grammar issue
 * @returns {string} - Formatted message
 */
export const getIssueMessage = (issue) => {
  const { message, context, offset, length, replacements } = issue;
  const contextText = context?.text || '';
  const highlight = '^'.repeat(length || 1);
  const pointer = ' '.repeat(offset) + highlight;
  
  let suggestionText = '';
  if (replacements && replacements.length > 0) {
    suggestionText = `\nSuggestion: ${replacements[0]}`;
  }
  
  return `${message}${suggestionText}\n\n${contextText}\n${pointer}`;
};
