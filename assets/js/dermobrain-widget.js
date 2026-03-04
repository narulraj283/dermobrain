/**
 * DermoBrain Embeddable Widget
 * Add this script to your dermatology practice website to display your DermoBrain profile.
 * Usage: <script src="https://dermobrain.com/assets/js/dermobrain-widget.js" data-npi="YOUR_NPI"></script>
 */
(function() {
    'use strict';

    const script = document.currentScript;
    const npi = script.getAttribute('data-npi');
    const theme = script.getAttribute('data-theme') || 'light';
    const width = script.getAttribute('data-width') || '100%';
    const articleCount = parseInt(script.getAttribute('data-articles') || '3', 10);

    if (!npi) {
        console.error('DermoBrain Widget: data-npi attribute is required');
        return;
    }

    const colors = theme === 'dark'
        ? { bg: '#1a1a1a', text: '#fff', secondary: '#ccc', accent: '#1A6B54', border: '#333', cardBg: '#222' }
        : { bg: '#fff', text: '#1a1a1a', secondary: '#666', accent: '#1A6B54', border: '#eee', cardBg: '#f8f9fa' };

    const container = document.createElement('div');
    container.id = 'dermobrain-widget';
    container.style.cssText = `max-width:${width === '100%' ? '100%' : width + 'px'};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:${colors.bg};border:1px solid ${colors.border};border-radius:12px;overflow:hidden;`;

    container.innerHTML = `
        <div style="padding:20px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                <div style="width:48px;height:48px;background:${colors.accent};border-radius:50%;display:flex;align-items:center;justify-content:center;">
                    <span style="color:white;font-size:1.2rem;font-weight:700;">D</span>
                </div>
                <div>
                    <div style="font-weight:700;color:${colors.text};font-size:1.1rem;">DermoBrain</div>
                    <div style="color:${colors.secondary};font-size:0.85rem;">Trusted Dermatology Information</div>
                </div>
            </div>
            <div id="dermobrain-profile" style="padding:16px;background:${colors.cardBg};border-radius:8px;margin-bottom:16px;">
                <p style="color:${colors.secondary};font-size:0.9rem;margin:0;">Loading practice profile...</p>
            </div>
            <div id="dermobrain-articles" style="margin-bottom:16px;"></div>
            <div style="text-align:center;padding-top:12px;border-top:1px solid ${colors.border};">
                <a href="https://dermobrain.com/find-a-dermatologist/" target="_blank" rel="noopener"
                   style="color:${colors.accent};text-decoration:none;font-size:0.85rem;font-weight:600;">
                    Powered by DermoBrain.com
                </a>
            </div>
        </div>
    `;

    script.parentNode.insertBefore(container, script.nextSibling);

    // Attempt to load profile data
    const profileDiv = document.getElementById('dermobrain-profile');
    profileDiv.innerHTML = `
        <p style="margin:0 0 8px;font-weight:600;color:${colors.text};">Practice Profile</p>
        <p style="margin:0;color:${colors.secondary};font-size:0.9rem;">
            Visit <a href="https://dermobrain.com/find-a-dermatologist/" target="_blank" rel="noopener" style="color:${colors.accent};">DermoBrain</a>
            to view the full profile and find dermatologists near you.
        </p>
    `;

    // Show educational articles
    const articlesDiv = document.getElementById('dermobrain-articles');
    const sampleArticles = [
        { title: 'Understanding Your Skin Type', url: '/skincare/science/' },
        { title: 'When to See a Dermatologist', url: '/guides/' },
        { title: 'Skin Cancer Warning Signs', url: '/medical-dermatology/skin-cancer/' }
    ];

    let articlesHTML = `<p style="margin:0 0 10px;font-weight:600;color:${colors.text};font-size:0.95rem;">Patient Education</p>`;
    sampleArticles.slice(0, articleCount).forEach(article => {
        articlesHTML += `
            <a href="https://dermobrain.com${article.url}" target="_blank" rel="noopener"
               style="display:block;padding:10px;margin-bottom:6px;background:${colors.cardBg};border-radius:6px;color:${colors.accent};text-decoration:none;font-size:0.9rem;">
                ${article.title} &rarr;
            </a>`;
    });
    articlesDiv.innerHTML = articlesHTML;
})();
