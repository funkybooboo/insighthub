import React from 'react';
import {
    type RagConfig,
    type CreateRagConfigRequest,
    type VectorRagConfig,
    type GraphRagConfig,
} from '../../types/workspace';
import VectorRagConfigForm from './VectorRagConfigForm';
import GraphRagConfigForm from './GraphRagConfigForm';

interface RagConfigFormProps {
    initialConfig?: Partial<RagConfig> | Partial<CreateRagConfigRequest>;
    onConfigChange: (config: Partial<CreateRagConfigRequest>) => void;
    readOnly?: boolean;
}



const RagConfigForm: React.FC<RagConfigFormProps> = ({
    initialConfig = {},
    onConfigChange,
    readOnly = false,
}) => {
    // Determine RAG type from config
    const ragType = initialConfig.retriever_type || 'vector';

    // Delegate to specific form based on RAG type
    if (ragType === 'graph') {
        return (
            <GraphRagConfigForm
                initialConfig={initialConfig as Partial<GraphRagConfig>}
                onConfigChange={(config) => onConfigChange({ ...config, retriever_type: 'graph' })}
                readOnly={readOnly}
            />
        );
    } else {
        return (
            <VectorRagConfigForm
                initialConfig={initialConfig as Partial<VectorRagConfig>}
                onConfigChange={(config) => onConfigChange({ ...config, retriever_type: 'vector' })}
                readOnly={readOnly}
            />
        );
    }
};

export default RagConfigForm;
