/**
 * Converts a Python datetime string to a human readable format
 * @param dateTimeStr - Datetime string in format 'YYYY-MM-DDTHH:MM:SS.NNNNNN'
 * @returns Human readable datetime string (e.g., "February 5, 2025 at 12:00 PM")
 */
export function formatDateTime(dateTimeStr: string): string {
    try {
        const date = new Date(dateTimeStr);
        
        // Check if the date is valid
        if (isNaN(date.getTime())) {
            return "Invalid datetime format";
        }

        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        }).replace(',', ' at');
    } catch {
        return "Invalid datetime format";
    }
}

export function unixToPythonDatetimeString(unixTimestamp: number): string {
    const date = new Date(unixTimestamp);
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

/**
 * Converts a Python datetime string to Unix timestamp (milliseconds)
 * @param pythonDateStr - Datetime string in format 'YYYY-MM-DDTHH:MM:SS.NNNNNN'
 * @returns Unix timestamp in milliseconds
 */
export function pythonDateToUnixTime(pythonDateStr: string): number {
    try {
        const date = new Date(pythonDateStr);
        
        // Check if the date is valid
        if (isNaN(date.getTime())) {
            throw new Error("Invalid datetime format");
        }

        return date.getTime();
    } catch (error) {
        throw new Error("Failed to convert datetime string to Unix timestamp");
    }
}

export function proposalStatus(status: string, end_date: string){
    console.log('status', status);
    console.log('end_date', end_date);
}

/**
 * Safely truncates HTML content while preserving tag structure
 * @param html - HTML content to truncate
 * @param maxLength - Maximum length of text content
 * @returns Truncated HTML string with preserved tag structure
 */
export function truncateHtml(html: string, maxLength: number): string {
    // Create a temporary div to parse HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    
    // If text content is already shorter than maxLength, return original
    if ((tempDiv.textContent || '').length <= maxLength) {
        return html;
    }
    
    // Parse the HTML structure
    const parseContent = (node: Node, currentLength = 0): { length: number, shouldStop: boolean } => {
        let length = currentLength;
        
        for (let i = 0; i < node.childNodes.length; i++) {
            const child = node.childNodes[i];
            
            if (child.nodeType === Node.TEXT_NODE) {
                const text = child.textContent || '';
                if (length + text.length > maxLength) {
                    // Find the last sentence end before maxLength
                    const remainingLength = maxLength - length;
                    const textSlice = text.slice(0, remainingLength);
                    
                    // Try to find the last sentence end (., !, or ?)
                    const lastSentenceEnd = Math.max(
                        textSlice.lastIndexOf('. '),
                        textSlice.lastIndexOf('! '),
                        textSlice.lastIndexOf('? ')
                    );
                    
                    // If no sentence end is found, find the last complete word
                    const lastSpaceIndex = textSlice.lastIndexOf(' ');
                    
                    // Determine where to truncate
                    let truncateIndex;
                    if (lastSentenceEnd > 0) {
                        truncateIndex = lastSentenceEnd + 1; // Include the period
                    } else if (lastSpaceIndex > 0) {
                        truncateIndex = lastSpaceIndex;
                    } else {
                        truncateIndex = remainingLength;
                    }
                    
                    child.textContent = text.slice(0, truncateIndex);
                    
                    // Remove remaining siblings
                    while (node.childNodes.length > i + 1) {
                        node.removeChild(node.childNodes[i + 1]);
                    }
                    return { length: maxLength, shouldStop: true };
                }
                length += text.length;
            } else if (child.nodeType === Node.ELEMENT_NODE) {
                const result = parseContent(child, length);
                length = result.length;
                if (result.shouldStop) {
                    // Remove remaining siblings
                    while (node.childNodes.length > i + 1) {
                        node.removeChild(node.childNodes[i + 1]);
                    }
                    return { length, shouldStop: true };
                }
            }
        }
        
        return { length, shouldStop: false };
    };
    
    parseContent(tempDiv);
    return tempDiv.innerHTML;
}

/**
 * Processes proposal metrics data and returns formatted proposal data
 * @param proposals - Array of proposal objects
 * @param metrics - Array of metric objects
 * @returns Object with processed proposal data including metrics
 */
export function processProposalMetrics(proposals: any[], metrics: any[]): any[] {
    const proposal_data: any[] = proposals.reduce((acc, proposal) => {
        acc[proposal.id] = { proposal };
        const proposal_metrics = metrics.filter(
            (metric) => metric.key.split(":")[1] === proposal.id
        );
        acc[proposal.id].metrics = proposal_metrics.reduce((acc, metric) => {
            const metric_key = metric.key.split(":")[2];
            acc[metric_key] = metric.value;
            return acc;
        }, {});
        return acc;
    }, {});

    console.log({ proposal_data });

    // Calculate totals for each proposal
    for (let proposal of Object.values(proposal_data)) {
        // if (!proposal.metrics.pow_abstain) {
        //     proposal.metrics = {
        //         pow_abstain: 0,
        //         pow_against: 0,
        //         pow_for: 0,
        //         total_abstain: 0,
        //         total_against: 0,
        //         total_for: 0,
        //     };
        // }
        
        proposal.metrics.total_votes =
            Number(proposal.metrics.total_for) +
            Number(proposal.metrics.total_against) +
            Number(proposal.metrics.total_abstain);
            
        proposal.metrics.pow_total =
            Number(proposal.metrics.pow_for) +
            Number(proposal.metrics.pow_against) +
            Number(proposal.metrics.pow_abstain);
    }

    return proposal_data;
}
