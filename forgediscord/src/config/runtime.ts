export interface RuntimeConfig {
  env: string;
  port: number;
  logLevel: string;
  discordBotToken: string;
  discordApplicationId: string;
  discordGuildId: string;
  openClawBaseUrl?: string;
  openClawApiKey?: string;
  dataDir: string;
  auditDir: string;
  jobsDir: string;
}

export function loadRuntimeConfig(): RuntimeConfig {
  return {
    env: process.env.FORGEDISCORD_ENV || 'development',
    port: Number(process.env.FORGEDISCORD_PORT || 4205),
    logLevel: process.env.LOG_LEVEL || 'info',
    discordBotToken: process.env.DISCORD_BOT_TOKEN || '',
    discordApplicationId: process.env.DISCORD_APPLICATION_ID || '',
    discordGuildId: process.env.DISCORD_GUILD_ID || '',
    openClawBaseUrl: process.env.OPENCLAW_BASE_URL,
    openClawApiKey: process.env.OPENCLAW_API_KEY,
    dataDir: process.env.FORGEDISCORD_DATA_DIR || './data',
    auditDir: process.env.FORGEDISCORD_AUDIT_DIR || './data/audit',
    jobsDir: process.env.FORGEDISCORD_JOBS_DIR || './data/jobs',
  };
}
