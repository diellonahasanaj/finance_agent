// Type declarations for the API module
declare module '../services/api' {
  interface AxiosInstance {
    get(url: string): Promise<{ data: any }>;
    post(url: string, data?: any): Promise<{ data: any }>;
    put(url: string, data?: any): Promise<{ data: any }>;
    delete(url: string): Promise<{ data: any }>;
  }
  
  const api: AxiosInstance;
  export default api;
}

// Also allow any .js imports
declare module "*.js" {
  const value: any;
  export default value;
}
