import type { APIRoute } from 'astro';
import Database from "better-sqlite3";
import path from "path";
import fs from "fs";

// Function to escape XML special characters
const escapeXml = (unsafe: string): string => {
  return unsafe.replace(/[<>&'"]/g, (c) => {
    switch (c) {
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '&': return '&amp;';
      case "'": return '&apos;';
      case '"': return '&quot;';
      default: return c;
    }
  });
};

// Generate slugs in the same way as your pages
const generateSlug = (name: string): string => {
  return name
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-");
};

export const GET: APIRoute = async ({ site }) => {
  if (!site) {
    return new Response("Site URL not configured", { status: 500 });
  }
  
  const baseUrl = site.toString();
  let urls: { loc: string; priority: string; }[] = [];
  
  // Add the main index page with high priority
  urls.push({
    loc: baseUrl,
    priority: "1.0" // Highest priority
  });
  
  // Get dynamic pages from the database
  try {
    const dbRelativePath = "database/spacecraft_thermal.db";
    const dbPath = path.resolve(process.cwd(), dbRelativePath);
    
    if (!fs.existsSync(dbPath)) {
      console.error("Database file not found for sitemap generation");
    } else {
      const db = new Database(dbPath, { readonly: true });
      
      // Query to get all required page data
      const stmt = db.prepare(`
        SELECT
          sc.spacecraft_name, 
          tao.analysis_object
        FROM thermal_analysis_entry te
        JOIN thermal_analysis_object tao ON te.object_id = tao.object_id
        JOIN spacecraft sc ON tao.spacecraft_id = sc.spacecraft_id
      `);
      
      const entries = stmt.all() as { spacecraft_name: string; analysis_object: string }[];
      
      // Add each dynamic page with lower priority
      entries.forEach(entry => {
        const spacecraftSlug = generateSlug(entry.spacecraft_name);
        const objectSlug = generateSlug(entry.analysis_object);
        const combinedSlug = `${spacecraftSlug}-${objectSlug}`;
        
        urls.push({
          loc: `${baseUrl}${combinedSlug}/`,
          priority: "0.5" // Lower priority for detail pages
        });
      });
      
      db.close();
    }
  } catch (error) {
    console.error("Error generating sitemap:", error);
  }

  // Create XML content
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(url => `  <url>
    <loc>${escapeXml(url.loc)}</loc>
    <priority>${url.priority}</priority>
  </url>`).join('\n')}
</urlset>`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml',
    },
  });
};