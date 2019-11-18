
#include "ModelBuilder.h"
#include "RooCategory.h"

void ModelBuilder::add_cut(std::string region,std::string ecut){
  extracuts[region]+=ecut;
}

void ModelBuilder::saveHist(TH1F *histogram){
    histogram->SetDirectory(0);
    fOut->WriteTObject(histogram);
}

void ModelBuilder::save(){
  std::map<std::string, TH1F*>::iterator it = save_hists.begin();
  for (;it!=save_hists.end();it++){
    //fOut->WriteTObject((*it).second);
    saveHist((*it).second);
  }

  std::map<std::string, RooDataSet*>::iterator itd = save_datas.begin();
  for (;itd!=save_datas.end();itd++){
    if (!wspace->data((*itd).second->GetName())) wspace->import(*((*itd).second));
    // should also make the basic dataset into a histogram for each additional var
    for (std::map<std::string,TH1F*>::iterator additional_var = additional_vars.begin()
        ; additional_var!=additional_vars.end()
	; additional_var++){
    	std::string var = additional_var->first;
    	TH1F *tmph = additional_var->second;
    	TH1F *hist_c = (TH1F*)generateTemplate(tmph,(RooFormulaVar*) 0
   	  , *(wspace->var(varstring.c_str()))
	  , (*itd).second
	  ,0,1, var, var); // extension is var name
     //fOut->WriteTObject(hist_corrected);
    	saveHist(hist_c);
    }
  }

  fOut->cd();
  //wspace->Write();
  fOut->WriteTObject(wspace);
  fOut->Write();
  fOut->SaveSelf(kTRUE);
}

bool ModelBuilder::has_process(ControlRegion &cr,std::string proc){
   bool ret = false;
   std::vector<std::pair<std::string, int> >::iterator it = cr.procs.begin();
   for (;it!=cr.procs.end();it++){
	if ((*it).first==proc) { 
		ret=true;
		break;
	}
   }
   return ret;
}
int ModelBuilder::process_type(ControlRegion &cr,std::string proc){
   std::vector<std::pair<std::string, int> >::iterator it = cr.procs.begin();
   for (;it!=cr.procs.end();it++){
	if ((*it).first==proc) { 
		return (*it).second;
	}
   }
   std::cout<< "Error - No Process Found -- " << proc  << std::endl;
   return 0;
}
void ModelBuilder::apply_corrections(std::string correction, std::string region, std::string process, bool run_systematics){
   // For now just run one, but of course can correct ALL processes if we need;
   // Find and import the dataset region_process
   std::map<std::string,RooDataSet*>::iterator it = save_datas.find(region+std::string("_")+process);

   wspace->import(*(*it).second);
   TH1F *hist_corrected = (TH1F*)generateTemplate(lTmp, (RooFormulaVar*)wspace->function(correction.c_str())
   	, *(wspace->var(varstring.c_str()))
	, (RooDataSet*) wspace->data(Form("%s_%s",region.c_str(),process.c_str()))
	,1,1);
     //fOut->WriteTObject(hist_corrected);
   saveHist(hist_corrected);


   for (std::map<std::string,TH1F*>::iterator additional_var = additional_vars.begin()
        ; additional_var!=additional_vars.end()
	; additional_var++){
     std::string var = additional_var->first;
     TH1F *tmph = additional_var->second;
     TH1F *hist_c = (TH1F*)generateTemplate(tmph,(RooFormulaVar*)wspace->function(correction.c_str())
   	, *(wspace->var(varstring.c_str()))
	, (RooDataSet*) wspace->data(Form("%s_%s",region.c_str(),process.c_str()))
	,1,1,var, var); // extension is same name as var
     //fOut->WriteTObject(hist_corrected);
     saveHist(hist_c);
   }

   //save_datas.erase(it);

   if (! run_systematics) return;
   // Systematics
   std::vector<TH1F> v_th1f_;
   std::cout << " Generating Systematics " << std::endl;
   generateVariations(lTmp,(RooFitResult*)fOut->Get(Form("fitResult_%s",correction.c_str()))
   	,(RooFormulaVar*)wspace->function(correction.c_str())
	,wspace->var(varstring.c_str()),v_th1f_,wspace,region+std::string("_")+process,fOut);

   // Book saving of histograms
   for (std::vector<TH1F>::iterator its = v_th1f_.begin();its!=v_th1f_.end();its++){
      // rename to include category name so that combine doesn't correlate them!
      (*its).SetName(Form("%s_%s",catname.c_str(),its->GetName()));
      saveHist(&(*its));
   }


}

void ModelBuilder::addSample(std::string name, std::string region, std::string process, bool is_mc, bool is_signal, bool saveDataset){
 
   TH1F *tmp_hist;

   if (! fIn->Get(name.c_str())){
       std::cout << Form("Error, no tree %s found in %s", name.c_str(), fIn->GetName()) << std::endl;
       assert(0);
   }

   // This is needed to make all things into a Dataset (for the fitting)
   std::cout << "Appending Sample " << name << std::endl;

   RooDataSet *tmp_data;

   RooRealVar *var    = wspace->var(varstring.c_str());
   RooRealVar *weight = wspace->var(weightname.c_str());

   RooArgSet treevariables(*var,*weight);
   // List all branches in the tree and add them as variables 
   TObjArray *branches = (TObjArray*) ((TTree*)fIn->Get(name.c_str()))->GetListOfBranches();
   TIter next(branches); TBranch *br;
   while ( (br = (TBranch*)next()) ){
       const char *brname = br->GetName();
       if ( std::strcmp(brname,weightname.c_str())!=0 && std::strcmp(brname,varstring.c_str())!=0 ){
           RooRealVar *vartmp = new RooRealVar(brname,brname,0,1); vartmp->removeRange();
           //std::cout << "Seen variable " << vartmp->GetName() <<  std::endl;
           if (strncmp (vartmp->GetName(),"gSM",3) == 0)
               continue;
           if (strncmp (vartmp->GetName(),"gDM",3) == 0)
               continue;
           if (strncmp (vartmp->GetName(),"couplingwgt",11) == 0)
               continue;
           if (strncmp (vartmp->GetName(),"id",2) == 0)
               continue;
           if (strncmp (vartmp->GetName(),"genWeight",9) == 0)
               continue;
           if (strncmp (vartmp->GetName(),"weightPU",8) == 0)
               continue;
           if (strncmp (vartmp->GetName(),"weightTurnOn",12) == 0)
               continue;
           //std::cout << "Adding variable " << vartmp->GetName() <<  std::endl;
           treevariables.add(*vartmp);
       }
   }
   /**************************************************************************/
   if (! (wspace->genobj("treevars"))) {
       //wspace->import(treevariables,"treevars");
       wspace->import(treevariables);
   }
   
   std::string lcutstring = cutstring;
   std::map<std::string,std::string>::iterator it_ecut = extracuts.find(region);
   if ( it_ecut != extracuts.end() ) {
       lcutstring+=" && "+(*it_ecut).second;
       // Also allow only a specific process to be cut 
   }
   it_ecut = extracuts.find(process);
   if ( it_ecut != extracuts.end() ) {	
   	   lcutstring+=" && "+(*it_ecut).second;
   }

   std::cout << " CUT STRING FOR " << process <<  ", in " << region  << " : " << lcutstring.c_str() << std::endl;
   if (is_mc) {
       tmp_hist = (TH1F*)generateTemplate(lTmp,(TTree *)fIn->Get(name.c_str()),varstring,weightname,lcutstring,Form("_tmphist%s",catname.c_str()));
       // Zeynep Test
       tmp_hist = DrawOverflow(tmp_hist);
       if (saveDataset)  tmp_data = new RooDataSet("tmpdata","dataset",treevariables,RooFit::Import(*(TTree*)fIn->Get(name.c_str())),RooFit::Cut(lcutstring.c_str()),RooFit::WeightVar(weightname.c_str()));
   } else {
       tmp_hist = (TH1F*)generateTemplate(lTmp,(TTree *)fIn->Get(name.c_str()),varstring,"",lcutstring,Form("_tmphist%s",catname.c_str()));
       if (saveDataset)  tmp_data = new RooDataSet("tmpdata","dataset",treevariables,RooFit::Import(*(TTree*)fIn->Get(name.c_str())),RooFit::Cut(lcutstring.c_str()));
       tmp_hist = DrawOverflow(tmp_hist);
   }
   
   std::map<std::string,ControlRegion>::iterator it_sample = v_samples.find(region);
   
   int type;
   if (!is_mc) type=0;
   else if (is_signal) type=-1;
   else type=1;
   
   TString tRegion = region;
   std::string pRegion = tRegion.Data();
   if (it_sample!=v_samples.end()) {
       bool proc_exists = has_process((*it_sample).second,process);
       if (proc_exists){
           save_hists[pRegion+std::string("_")+process]->Add(tmp_hist);
           if (saveDataset) {
               save_datas[pRegion+std::string("_")+process]->append(*tmp_data);
               std::cout << "Adding to existing sample -- " <<pRegion+std::string("_")+process << " -> " <<  name.c_str() << ", dataset=" << tmp_data->sumEntries()  << " histogram=" <<tmp_hist->Integral() << std::endl; 
           }
       } else {
           tmp_hist->SetName(Form("%s_%s",pRegion.c_str(),process.c_str()));
           if (saveDataset)  tmp_data->SetName(Form("%s_%s",pRegion.c_str(),process.c_str()));
           save_hists[pRegion+std::string("_")+process] = tmp_hist;
           if (saveDataset)  save_datas[pRegion+std::string("_")+process] = tmp_data;   
           ((*it_sample).second).procs.push_back(std::pair<std::string,int> (process,type));
         
       }
   }
   else {
       ControlRegion cregion;
       cregion.name = region;
       cregion.procs.push_back(std::pair<std::string,int> (process,type));
       v_samples[region] = cregion;
       
       tmp_hist->SetName(Form("%s_%s",pRegion.c_str(),process.c_str()));
       save_hists.insert(std::pair<std::string,TH1F*> (pRegion+std::string("_")+process,tmp_hist));
       if (saveDataset) {
           tmp_data->SetName(Form("%s_%s",pRegion.c_str(),process.c_str()));
           save_datas.insert(std::pair<std::string,RooDataSet*> (pRegion+std::string("_")+process,tmp_data));
       }
   } 
}
