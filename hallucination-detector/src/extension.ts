import * as vscode from 'vscode';

// ── Types ──────────────────────────────────────
interface EvidenceItem {
	source: string;
	text: string;
	verdict: string;
	relevance: number;
}

interface CheckResponse {
	original_claim: string;
	score: number;
	label: string;
	confidence: string;
	explanation: string;
	evidence: EvidenceItem[];
}

// ── Decoration types for underlines ───────────
let hallucinated: vscode.TextEditorDecorationType;
let uncertain: vscode.TextEditorDecorationType;
let grounded: vscode.TextEditorDecorationType;

export function activate(context: vscode.ExtensionContext) {

	console.log('Hallucination Detector is active');

	// ── Define underline colors ────────────────
	hallucinated = vscode.window.createTextEditorDecorationType({
		textDecoration: 'underline wavy red'
	});

	uncertain = vscode.window.createTextEditorDecorationType({
		textDecoration: 'underline wavy yellow'
	});

	grounded = vscode.window.createTextEditorDecorationType({
		textDecoration: 'underline wavy green'
	});

	// ── Register command ───────────────────────
	const command = vscode.commands.registerCommand(
		'hallucination-detector.check',
		async () => {

			const editor = vscode.window.activeTextEditor;
			if (!editor) {
				vscode.window.showErrorMessage('No active editor found');
				return;
			}

			// get selected text
			const selection = editor.selection;
			const text      = editor.document.getText(selection);

			if (!text.trim()) {
				vscode.window.showWarningMessage('Please select some text first');
				return;
			}

			// show loading message
			vscode.window.showInformationMessage('🔍 Checking for hallucinations...');

			try {
				// call backend
				const result = await checkClaim(text.trim());

				// apply underline decoration
				applyDecoration(editor, selection, result.label);

				// ── NEW: register hover tooltip ──
                const range = new vscode.Range(selection.start, selection.end);
                registerHoverProvider(context, result, range);

				// show result popup
				showResult(result);

			} catch (error) {
				vscode.window.showErrorMessage(
					'Could not connect to backend. Is it running on localhost:8000?'
				);
			}
		}
	);

	context.subscriptions.push(command);
}

// ── Call FastAPI backend ───────────────────────
async function checkClaim(claim: string): Promise<CheckResponse> {
	const response = await fetch('https://rithiktiwari33-hallucination-detector.hf.space/api/check', {
		method:  'POST',
		headers: { 'Content-Type': 'application/json' },
		body:    JSON.stringify({ claim })
	});

	if (!response.ok) {
		throw new Error(`Backend error: ${response.status}`);
	}

	return response.json() as Promise<CheckResponse>;
}

// ── Apply colored underline to selected text ───
function applyDecoration(
	editor: vscode.TextEditor,
	selection: vscode.Selection,
	label: string
) {
	const range = [{ range: selection }];

	// clear previous decorations
	editor.setDecorations(hallucinated, []);
	editor.setDecorations(uncertain,    []);
	editor.setDecorations(grounded,     []);

	// apply new decoration based on label
	if (label === 'hallucinated') {
		editor.setDecorations(hallucinated, range);
	} else if (label === 'uncertain') {
		editor.setDecorations(uncertain, range);
	} else {
		editor.setDecorations(grounded, range);
	}
}

// ── Show result as popup ───────────────────────
function showResult(result: CheckResponse) {
	const emoji = result.label === 'hallucinated' ? '❌' :
	              result.label === 'grounded'     ? '✅' : '⚠️';

	const score = (result.score * 100).toFixed(0);

	// top level message
	const message = `${emoji} ${result.label.toUpperCase()} — Score: ${score}% | ${result.explanation}`;

	// show with evidence details
	vscode.window.showInformationMessage(
		message,
		'Show Evidence'
	).then(selection => {
		if (selection === 'Show Evidence') {
			showEvidence(result);
		}
	});
}

// ── Show evidence in output panel ─────────────
function showEvidence(result: CheckResponse) {
	const channel = vscode.window.createOutputChannel('Hallucination Detector');
	channel.clear();

	channel.appendLine(`${'='.repeat(60)}`);
	channel.appendLine(`CLAIM: ${result.original_claim}`);
	channel.appendLine(`SCORE: ${(result.score * 100).toFixed(0)}% | LABEL: ${result.label.toUpperCase()} | CONFIDENCE: ${result.confidence}`);
	channel.appendLine(`${'='.repeat(60)}\n`);

	channel.appendLine('EVIDENCE FOUND:\n');
	result.evidence.forEach((e, i) => {
		const icon = e.verdict === 'CONTRADICTS' ? '❌' :
		             e.verdict === 'SUPPORTS'    ? '✅' : '⚠️';
		channel.appendLine(`${i + 1}. ${icon} ${e.verdict}`);
		channel.appendLine(`   Source:    ${e.source}`);
		channel.appendLine(`   Relevance: ${(e.relevance * 100).toFixed(0)}%`);
		channel.appendLine(`   Text:      ${e.text}\n`);
	});

	channel.show();
}

export function deactivate() {}

// ── Register hover provider ────────────────────
function registerHoverProvider(context: vscode.ExtensionContext, result: CheckResponse, range: vscode.Range) {
	
	const emoji = result.label === 'hallucinated' ? '❌' :
	              result.label === 'grounded'     ? '✅' : '⚠️';

	const score = (result.score * 100).toFixed(0);

	// build markdown tooltip
	const markdown = new vscode.MarkdownString();
	markdown.isTrusted = true;
	markdown.appendMarkdown(`### ${emoji} Hallucination Detector\n\n`);
	markdown.appendMarkdown(`**Score:** ${score}% | **Label:** ${result.label.toUpperCase()} | **Confidence:** ${result.confidence}\n\n`);
	markdown.appendMarkdown(`**Explanation:** ${result.explanation}\n\n`);
	markdown.appendMarkdown(`---\n\n`);
	markdown.appendMarkdown(`**Evidence:**\n\n`);

	result.evidence.slice(0, 3).forEach(e => {
		const icon = e.verdict === 'CONTRADICTS' ? '❌' :
		             e.verdict === 'SUPPORTS'    ? '✅' : '⚠️';
		markdown.appendMarkdown(`${icon} **${e.verdict}** — ${e.text.slice(0, 80)}...\n\n`);
	});

	// register hover for this specific range
	const hover = vscode.languages.registerHoverProvider('*', {
		provideHover(document, position) {
			if (range.contains(position)) {
				return new vscode.Hover(markdown, range);
			}
		}
	});

	// dispose previous hover and register new one
	context.subscriptions.push(hover);
}