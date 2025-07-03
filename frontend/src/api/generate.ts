import axiosInstance from "./axiosInstance";
import { GenerateResponse } from "../types/apiTypes";

// export const generateResponse = async (
//   query: string,
//   company: string,
//   subQuestions: SubQuestion[]
// ): Promise<GenerateResponse> => {
//   const requestBody: GenerateRequestBody = {
//     query,
//     company,
//     sub_questions: subQuestions,
//     db_table: "pwc_json_meddpicc",
//   };

//   try {
//     const response = await axiosInstance.post<GenerateResponse>(
//       "/generate",
//       requestBody
//     );
//     return response.data;
//   } catch (error) {
//     console.error("Error making request:", error);
//     throw error;
//   }
// };

export const generateResponse = async (
  query: any
): Promise<GenerateResponse> => {
  const requestBody = JSON.stringify(query);
  // console.log("requestBody", requestBody);
  try {
    const response = await axiosInstance.post<GenerateResponse>(
      "/generate",
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error making request:", error);
    throw error;
  }
};
