import React from 'react';
import { type VectorRagConfig } from '../../types/workspace';
import VectorRagConfigForm from './VectorRagConfigForm';

interface RagConfigFormProps {
    initialConfig?: Partial<VectorRagConfig>;
    onConfigChange: (config: Partial<VectorRagConfig>) => void;
    readOnly?: boolean;
}

const RagConfigForm: React.FC<RagConfigFormProps> = ({
    initialConfig = {},
    onConfigChange,
    readOnly = false,
}) => {
    // For now, only support Vector RAG in workspace creation
    return (
        <VectorRagConfigForm
            initialConfig={initialConfig}
            onConfigChange={onConfigChange}
            readOnly={readOnly}
        />
    );
};

export default RagConfigForm;
