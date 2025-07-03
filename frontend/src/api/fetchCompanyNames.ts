import { CompanyName } from "../types/apiTypes";
import axiosInstance from "./axiosInstance";

export const fetchCompanyNames = async (): Promise<CompanyName[]> => {
  try {
    const response = await axiosInstance.get<CompanyName[]>("/companies/");
    return response.data;
  } catch (error) {
    console.error("Error fetching company names:", error);
    throw error;
  }
};
