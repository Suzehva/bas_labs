import { z } from "zod";
import axios from "axios";
import { PythonShell} from 'python-shell';
import * as path from 'path';


// this.pythonShell = new PythonShell('worker.py', {
//   mode: 'text',
//   pythonPath: 'python3',
//   pythonOptions: ['-u'],
//   scriptPath: './python_scripts'
// });
type PythonShellOptions = {
  args: string[];
};

import {
  defineDAINService,
  ToolConfig,
} from "@dainprotocol/service-sdk";

import { CardUIBuilder, TableUIBuilder, MapUIBuilder } from "@dainprotocol/utils";

const find_company_climate_initiatives: ToolConfig = {
  id: "net_zero_tracker",
  name: "Find climate initiatives",
  description: "Finds the climate initiatives a company is doing",
  input: z
    .object({
      companyName: z.string().describe("Company name"),
    })
    .describe("Input parameters for the company climate initiative request"),
  output: z
    .object({
      company_climate_information: z.string().describe("Company information on climate initiatives"),
    }),
  pricing: { pricePerUse: 0, currency: "USD" },

  handler: async ({ companyName }, agentInfo, context) => {
    console.log(
      `User / Agent ${agentInfo.id} requested information from net_zero_tracker for company ${companyName}`
    );
    

    function scrape_netzero(companyName: string): Promise<string> {
      const options: PythonShellOptions = {
        args: [companyName],
      };
      const scriptPath = path.join(__dirname, 'scrape_netzero.py');
    
      return PythonShell.run(scriptPath, options) // Using Promise-based API
        .then((result) => {
          // Since result is an array of strings (one for each printed line),
          // we join them together
          return result.join('\n');
        })
        .catch((err) => {
          console.error("Error executing Python script:", err);
          throw err;2 
        });
    }
    

    let company_info: string; 
    
    try {
      company_info = await scrape_netzero(companyName);
      console.log("Python script result:", company_info);
    } catch (error) {
        console.error("Error:", error);
    }

    const cardUI = new CardUIBuilder()
      .title("Findings")
      .content("?")
      .build();


    return {
      text: `The information about the company ${companyName} is as follows: ${company_info}`,
      data: {
        company_climate_information: company_info,
      },
      ui: cardUI,
    };
  },
};


const dainService = defineDAINService({
  metadata: {
    title: "Climate match making DAIN Service",
    description:
      "A DAIN service for matching companies with climate initiatives using Selenium",
    version: "1.0.0",
    author: "Suze van Adrichem and Alice Heiman",
    tags: ["climate"],
    logo: "https://cdn-icons-png.flaticon.com/512/252/252035.png",
  },
  exampleQueries: [
   {
    category: "Climate",
    queries: [
      "What climate initiatives could my company Amazon use?",
      "We're a small company Scrapybara. What climate initiatives could we consider?",
    ],
   }
  ],
  identity: {
    apiKey: process.env.DAIN_API_KEY,
  },
  tools: [find_company_climate_initiatives],
});

dainService.startNode({ port: 2022 }).then(() => {
  console.log("Climate match making DAIN Service is running on port 2022");
});
