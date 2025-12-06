// ==UserScript==
// @name         Perplexity Local Agent Bridge
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  Integrates Perplexity AI with Local Agent for PC control
// @author       Fisterovna2
// @match        *://www.perplexity.ai/*
// @grant        GM_xmlhttpRequest
// @grant        GM_addStyle
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';
    const AGENT_URL = 'http://localhost:5000';
    
    // Add agent button to Perplexity UI
    function initAgent() {
        const btn = document.createElement('button');
        btn.id = 'local-agent-btn';
        btn.textContent = '🤖 Local Agent';
        btn.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9999;padding:10px 15px;background:#6366f1;color:white;border:none;border-radius:8px;cursor:pointer;font-weight:bold;';
        
        btn.addEventListener('click', showAgentPanel);
        document.body.appendChild(btn);
    }
    
    function showAgentPanel() {
        if (document.getElementById('agent-panel')) return;
        
        const panel = document.createElement('div');
        panel.id = 'agent-panel';
        panel.style.cssText = 'position:fixed;bottom:80px;right:20px;width:400px;background:white;border:2px solid #6366f1;border-radius:12px;box-shadow:0 10px 40px rgba(0,0,0,0.2);z-index:9998;padding:20px;';
        
        panel.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;">
                <h3 style="margin:0;color:#333;">Local Agent Control</h3>
                <button onclick="document.getElementById('agent-panel').remove()" style="background:none;border:none;font-size:20px;cursor:pointer;">×</button>
            </div>
            <textarea id="agent-input" placeholder="Enter your request..." style="width:100%;height:100px;padding:10px;border:1px solid #ddd;border-radius:6px;font-family:monospace;font-size:12px;resize:none;"></textarea>
            <button id="agent-send" style="width:100%;margin-top:10px;padding:10px;background:#6366f1;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:bold;">Send Request</button>
            <button id="agent-info" style="width:100%;margin-top:8px;padding:10px;background:#f59e0b;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:bold;">ℹ️ Info</button>
            <div id="agent-response" style="margin-top:15px;padding:10px;background:#f3f4f6;border-radius:6px;min-height:50px;max-height:150px;overflow-y:auto;font-family:monospace;font-size:11px;white-space:pre-wrap;word-break:break-word;"></div>
        `;
        
        document.body.appendChild(panel);
        
        document.getElementById('agent-send').addEventListener('click', sendToAgent);
        document.getElementById('agent-info').addEventListener('click', showInfo);
    }
    
    function sendToAgent() {
        const input = document.getElementById('agent-input').value;
        const response = document.getElementById('agent-response');
        
        if (!input.trim()) {
            response.textContent = 'Please enter a request';
            return;
        }
        
        response.textContent = 'Sending...';
        
        GM_xmlhttpRequest({
            method: 'POST',
            url: AGENT_URL + '/execute',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify({command: input}),
            onload: function(resp) {
                try {
                    const data = JSON.parse(resp.responseText);
                    response.textContent = data.result || 'Command executed';
                } catch(e) {
                    response.textContent = 'Response: ' + resp.responseText;
                }
            },
            onerror: function() {
                response.textContent = 'Error: Cannot reach Local Agent at ' + AGENT_URL;
            }
        });
    }
    
    function showInfo() {
        alert('Local Agent v2.0\n\nFeatures:\n✓ Create 3D models\n✓ Generate games\n✓ Execute Python code\n✓ Control PC safely\n\nAll actions require confirmation before execution.\n\nAgent running at: ' + AGENT_URL);
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAgent);
    } else {
        initAgent();
    }
})();
