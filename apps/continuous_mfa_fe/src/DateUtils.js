/**
 * Converts a Unix epoch timestamp to a formatted string in the browser's time zone.
 * @param {number} unixTimestamp - The Unix epoch timestamp (in seconds).
 * @returns {string} - The formatted date and time as MM/DD HH:MM AM/PM (no comma).
 */
export function formatDate(unixTimestamp) {

    if (!unixTimestamp) {
      return '';
    }
    // Format date and time with Intl.DateTimeFormat
    const formatter = new Intl.DateTimeFormat('en-US', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true, // Ensures AM/PM formatting
    });
  
    // Remove comma by splitting and joining
    return formatter
      .format(new Date(unixTimestamp * 1000))
      .replace(',', ''); // Removes the comma between date and time
  }