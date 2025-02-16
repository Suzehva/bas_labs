import { arrayOutputType, z } from "zod";
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

import { DainResponse, CardUIBuilder, TableUIBuilder, MapUIBuilder, LayoutUIBuilder } from "@dainprotocol/utils";
import { AgentInfo } from "@dainprotocol/service-sdk";

const find_company_climate_initiatives: ToolConfig = {
  id: "net_zero_tracker",
  name: "Find climate initiatives",
  description: "Finds the climate initiatives a company is doing",
  input: z
    .object({
      companyName: z.string().describe("Company name"),
    })
    .describe("Input parameters for the company climate initiative request. Make sure to provide the full company name and try different acronyms of the company name if the information returned is for the wrong company."),
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

    // const tableUI = new TableUIBuilder()
    //   .addColumns([
    //     { key: "name", header: "Name", type: "text" },
    //     { key: "value", header: "Value", type: "text" }
    //   ])
    //   .rows(company_info)
    //   .build();

    const summary = new CardUIBuilder()
      .setRenderMode("page")
      .title(`Climate Initiatives for ${companyName}`)
      .content(company_info)
      .build();

    const one_climate_initiative = new CardUIBuilder()
      .setRenderMode("page")
      .title(`Climate Initiatives for ${companyName}`)
      .content(company_info)
      .build();


    const fullUI = new CardUIBuilder()
      .setRenderMode("page")
      .title(`Climate Initiatives for ${companyName}`)
      .content(company_info)

      .addChild(summary).content(company_info)
      .addChild(one_climate_initiative).content(company_info)
      .addChild(one_climate_initiative).content(company_info)
      .addChild(one_climate_initiative).content(company_info)
      
      //.addChild(tableUI)
      
      .build();

    // const gridLayout = new LayoutUIBuilder()
    //   .setLayoutType("grid")
    //   .setColumns(3)
    //   .setGap(24)
    //   .setMargin("32px")
    //   .setBackgroundColor("#f5f5f5")
    //   .build();

    const super_basic_UI = new CardUIBuilder()
      //.title(`Climate Initiatives for ${companyName}`)
      //.content(company_info)
      .build();

    return new DainResponse({
      text: `This response includes data from net zero tracker, which tracks a company's climate's initiatives, for the company ${companyName}`,
      data: {
        company_climate_information: company_info,
      },
      ui: super_basic_UI,
    });
  },
};


const find_similar_companies: ToolConfig = {
  id: "nzdpu",
  name: "Find similar companies",
  description: "Finds companies similar to the company we are researching by using information about the sector and country the company is in. Use in combination with find_company_climate_initiatives to find what companies similar to the one we are researching are doing for their climate initiatives.",
  input: z
    .object({
      sector: z.string().describe("Sector the company is in"),
      country: z.string().describe("Country the company is located in"),
    })
    .describe("Input parameters for the similar companies request. If a company is located in multiple countries, ask user to provide only one"),
  output: z
    .object({
      similar_companies: z.array(z.string()).describe("A list of companies similar to the one we are researching. Use find_company_climate_initiatives to find what climate initiatives each company does"),
    }),
  pricing: { pricePerUse: 0, currency: "USD" },

  handler: async ({ sector,  country }, agentInfo, context) => {
    console.log(
      `User / Agent ${agentInfo.id} requested information from nzdpu to find similar compabies`
    );
    

    function scrape_nzdpu(sector: string, country: string): Promise<Array<string>> {
      const options: PythonShellOptions = {
        args: [sector, country],
      };
      const scriptPath = path.join(__dirname, 'scrape_nzdpu.py');
    
      return PythonShell.run(scriptPath, options) // Using Promise-based API
        .then((result) => {
          // Since result is an array of strings (one for each printed line),
          // we join them together
          return JSON.parse(result.join(''));
        })
        .catch((err) => {
          console.error("Error executing Python script:", err);
          throw err;2 
        });
    }
    

    let similar_comps: Array<string>; 
    try {
      similar_comps = await scrape_nzdpu(sector, country);
      console.log("Python script result:", similar_comps);
    } catch (error) {
        console.error("Error:", error);
    }

    const super_basic_UI = new CardUIBuilder()
      //.title(`Climate Initiatives for ${companyName}`)
      //.content(company_info)
      .build();

    return new DainResponse({
      text: `This response includes data from net zero tracker, which tracks a company's climate's initiatives in the sector ${sector} and country ${country}`,
      data: {
        similar_companies: similar_comps,
      },
      ui: super_basic_UI,
    });
  },
};

interface ServiceContext {
  id: string;              // Unique identifier
  name: string;           // Display name
  description: string;    // Description of the context
  getContextData: (agentInfo: AgentInfo) => Promise<string>;  // Context generator
}

const BASContext: ServiceContext = {
  id: "BAS_instructions",              // Unique identifier
  name: "BAS instructions",           // Display name
  description: "Instructions provided to agent BAS",    // Description of the context
  getContextData: async (agentInfo) => {
    
  return `
  You are an agent called BAS. You are helping a company (called THE USER) ideate potential climate initiative that align with the companies mission, sector and location. 
  To do so, you will research other similar companies (called THE INSPIRATIONS) using tools to find and report back information you find. Before you return to the company, fulfill the following requirements:
  1. Present three main topics for climate mitigation specific to THE USER
  2. For each topic, find three concrete climate initatives used by three different company INSPIRATIONS. These must be grounded from the INSPIRATIONS actual sustainability reports.
  3. Present the information in an engaging and professional way that highlights concrete steps THE USER can take to reduce their emissions. 
  
  Rules:
  - You must provide URLs to all sources that you use.
  - Aim to include climate actions that you have quantitative data on and that demonstrate reproducible action that leads to return on investment.

  If you do not have enough information to return this information, ask the company for more information and try again.
      `.trim();
  }
};

const dainService = defineDAINService({
  metadata: {
    title: "Climate match making DAIN Service",
    description:
      "A DAIN service for matching companies with climate initiatives.",
    version: "1.0.0",
    author: "Suze van Adrichem and Alice Heiman",
    tags: ["climate"],
    logo: "https://cdn-icons-png.flaticon.com/512/252/252035.png",
  },
  contexts: [BASContext],
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
  tools: [find_company_climate_initiatives, find_similar_companies],
});

dainService.startNode({ port: 2022 }).then(() => {
  console.log("Climate match making DAIN Service is running on port 2022");
});


/*
hi! I work at a startup that works in the tech sector in the United states. What are other companies in this space doing to help advance the climate?

*/;