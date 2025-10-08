import React from 'react';
import { FileText } from 'lucide-react';
import { Card } from '../ui/card';
import ContributionForm from './ContributionForm';

const ManualEntryFlow = () => {
  return (
    <div>
      <Card className="bg-[#1F1F1F] border-gray-700 p-6 mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-[#F5C518] rounded-full flex items-center justify-center">
            <FileText className="w-6 h-6 text-[#0F0F0F]" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Add Podcast Manually</h2>
            <p className="text-gray-400">Fill in the podcast details below</p>
          </div>
        </div>
      </Card>

      <ContributionForm 
        initialData={{}}
        mode="manual"
      />
    </div>
  );
};

export default ManualEntryFlow;