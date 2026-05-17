export const config = {
  API_BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
  IS_DEV: process.env.NODE_DEV === 'development',
  APP_NAME: 'Yefai',
};
