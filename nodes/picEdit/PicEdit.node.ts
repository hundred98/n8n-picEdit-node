import { IExecuteFunctions } from 'n8n-workflow';
import { INodeExecutionData, INodeType, INodeTypeDescription, NodeExecutionWithMetadata, NodeOperationError } from 'n8n-workflow';
import { spawn } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import csvParser = require('csv-parser');

export class PicEdit implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'PicEdit',
        name: 'picEdit',
        icon: 'file:picEdit.svg',
        group: ['transform'],
        version: 1,
        description: 'Generate images with text and image overlays',
        defaults: {
            name: 'PicEdit',
        },
        inputs: ['main'],
        outputs: ['main'],
        properties: [
            {
                displayName: 'Operation',
                name: 'operation',
                type: 'options',
                noDataExpression: true,
                options: [
                    {
                        name: 'Create Canvas',
                        value: 'createCanvas',
                        description: 'Create a new canvas',
                    },
                    {
                        name: 'Add Text',
                        value: 'addText',
                        description: 'Add text to canvas',
                    },
                    {
                        name: 'Add Image',
                        value: 'addImage',
                        description: 'Add image to canvas',
                    },
                ],
                default: 'createCanvas',
            },

            // Create Canvas
            {
                displayName: 'Canvas Type',
                name: 'canvasType',
                type: 'options',
                displayOptions: {
                    show: {
                        operation: [
                            'createCanvas',
                        ],
                    },
                },
                options: [
                    {
                        name: 'Blank',
                        value: 'blank',
                    },
                    {
                        name: 'From Image',
                        value: 'image',
                    },
                ],
                default: 'blank',
                description: 'Type of canvas to create',
            },
            {
                displayName: 'Width',
                name: 'width',
                type: 'number',
                displayOptions: {
                    show: {
                        operation: [
                            'createCanvas',
                        ],
                        canvasType: [
                            'blank',
                        ],
                    },
                },
                typeOptions: {
                    minValue: 1,
                },
                default: 800,
                description: 'Width of the canvas in pixels',
            },
            {
                displayName: 'Height',
                name: 'height',
                type: 'number',
                displayOptions: {
                    show: {
                        operation: [
                            'createCanvas',
                        ],
                        canvasType: [
                            'blank',
                        ],
                    },
                },
                typeOptions: {
                    minValue: 1,
                },
                default: 600,
                description: 'Height of the canvas in pixels',
            },
            {
                displayName: 'Background Color',
                name: 'backgroundColor',
                type: 'color',
                displayOptions: {
                    show: {
                        operation: [
                            'createCanvas',
                        ],
                        canvasType: [
                            'blank',
                        ],
                    },
                },
                default: '#ffffff',
                description: 'Background color of the canvas',
            },
            {
                displayName: 'Image Path',
                name: 'imagePath',
                type: 'string',
                displayOptions: {
                    show: {
                        operation: [
                            'createCanvas',
                        ],
                        canvasType: [
                            'image',
                        ],
                    },
                },
                default: '',
                description: 'Path to the background image',
            },

            // Add Text
            {
                displayName: 'Text Source',
                name: 'textSource',
                type: 'options',
                displayOptions: {
                    show: {
                        operation: [
                            'addText',
                        ],
                    },
                },
                options: [
                    {
                        name: 'Manual',
                        value: 'manual',
                    },
                    {
                        name: 'CSV File',
                        value: 'csv',
                    },
                ],
                default: 'manual',
                description: 'Source of the text to add',
            },
            {
                displayName: 'Text',
                name: 'text',
                type: 'string',
                displayOptions: {
                    show: {
                        operation: [
                            'addText',
                        ],
                        textSource: [
                            'manual',
                        ],
                    },
                },
                default: '',
                description: 'Text to add to the canvas',
            },
            {
                displayName: 'Position X',
                name: 'positionX',
                type: 'number',
                displayOptions: {
                    show: {
                        operation: [
                            'addText',
                        ],
                        textSource: [
                            'manual',
                        ],
                    },
                },
                default: 0,
                description: 'X position of the text',
            },
            {
                displayName: 'Position Y',
                name: 'positionY',
                type: 'number',
                displayOptions: {
                    show: {
                        operation: [
                            'addText',
                        ],
                        textSource: [
                            'manual',
                        ],
                    },
                },
                default: 0,
                description: 'Y position of the text',
            },
            {
                displayName: 'Font Size',
                name: 'fontSize',
                type: 'number',
                displayOptions: {
                    show: {
                        operation: [
                            'addText',
                        ],
                        textSource: [
                            'manual',
                        ],
                    },
                },
                typeOptions: {
                    minValue: 1,
                },
                default: 24,
                description: 'Font size in pixels',
            },
            {
                displayName: 'Color',
                name: 'color',
                type: 'color',
                displayOptions: {
                    show: {
                        operation: [
                            'addText',
                        ],
                        textSource: [
                            'manual',
                        ],
                    },
                },
                default: '#000000',
                description: 'Text color',
            },
            {
                displayName: 'Font Name',
                name: 'fontName',
                type: 'string',
                displayOptions: {
                    show: {
                        operation: [
                            'addText',
                        ],
                        textSource: [
                            'manual',
                        ],
                    },
                },
                default: '',
                description: 'Font name (leave empty for default font)',
            },
            {
                displayName: 'Alignment',
                name: 'alignment',
                type: 'options',
                displayOptions: {
                    show: {
                        operation: [
                            'addText',
                        ],
                        textSource: [
                            'manual',
                        ],
                    },
                },
                options: [
                    {
                        name: 'Left',
                        value: 'left',
                    },
                    {
                        name: 'Center',
                        value: 'center',
                    },
                    {
                        name: 'Right',
                        value: 'right',
                    },
                ],
                default: 'left',
                description: 'Text alignment',
            },
            {
                displayName: 'CSV File Path',
                name: 'csvFilePath',
                type: 'string',
                displayOptions: {
                    show: {
                        operation: [
                            'addText',
                        ],
                        textSource: [
                            'csv',
                        ],
                    },
                },
                default: '',
                description: 'Path to the CSV file containing text data',
            },
            {
                displayName: 'CSV Format Info',
                name: 'csvFormatInfo',
                type: 'notice',
                displayOptions: {
                    show: {
                        operation: [
                            'addText',
                        ],
                        textSource: [
                            'csv',
                        ],
                    },
                },
                default: '',
                description: 'CSV columns: text,position_x,position_y,font_size,color,font_name,alignment,rotation,opacity',
            },

            // Add Image
            {
                displayName: 'Image Path',
                name: 'overlayImagePath',
                type: 'string',
                displayOptions: {
                    show: {
                        operation: [
                            'addImage',
                        ],
                    },
                },
                default: '',
                description: 'Path to the image file to overlay',
            },
            {
                displayName: 'Position X',
                name: 'imagePositionX',
                type: 'number',
                displayOptions: {
                    show: {
                        operation: [
                            'addImage',
                        ],
                    },
                },
                default: 0,
                description: 'X position of the image',
            },
            {
                displayName: 'Position Y',
                name: 'imagePositionY',
                type: 'number',
                displayOptions: {
                    show: {
                        operation: [
                            'addImage',
                        ],
                    },
                },
                default: 0,
                description: 'Y position of the image',
            },
            {
                displayName: 'Scale',
                name: 'scale',
                type: 'number',
                displayOptions: {
                    show: {
                        operation: [
                            'addImage',
                        ],
                    },
                },
                typeOptions: {
                    minValue: 0,
                    maxValue: 10,
                },
                default: 1,
                description: 'Scale factor for the image',
            },
            {
                displayName: 'Rotation',
                name: 'rotation',
                type: 'number',
                displayOptions: {
                    show: {
                        operation: [
                            'addImage',
                        ],
                    },
                },
                typeOptions: {
                    minValue: -360,
                    maxValue: 360,
                },
                default: 0,
                description: 'Rotation angle in degrees',
            },
        ],
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][] | NodeExecutionWithMetadata[][] | null> {
        const items = this.getInputData();
        const operation = this.getNodeParameter('operation', 0) as string;
        const returnItems: INodeExecutionData[] = [];

        for (let i = 0; i < items.length; i++) {
            try {
                let result: any;
                
                if (operation === 'createCanvas') {
                    result = await createCanvas.call(this, i);
                } else if (operation === 'addText') {
                    result = await addText.call(this, i, items[i].json);
                } else if (operation === 'addImage') {
                    result = await addImage.call(this, i, items[i].json);
                }

                returnItems.push({
                    json: result,
                });
            } catch (error: any) {
                if (this.continueOnFail()) {
                    returnItems.push({
                        json: {
                            error: error.message,
                        },
                        pairedItem: {
                            item: i,
                        },
                    });
                    return [returnItems];
                } else {
                    throw error;
                }
            }
        }

        return [returnItems];
    }
}

async function createCanvas(this: IExecuteFunctions, itemIndex: number): Promise<any> {
    const canvasType = this.getNodeParameter('canvasType', itemIndex) as string;
    
    const config: any = {
        mode: 'config',
        canvas: {},
        elements: [],
        outputFormat: 'base64'
    };

    if (canvasType === 'blank') {
        config.canvas = {
            width: this.getNodeParameter('width', itemIndex) as number,
            height: this.getNodeParameter('height', itemIndex) as number,
            backgroundColor: this.getNodeParameter('backgroundColor', itemIndex) as string,
        };
    } else {
        const imagePath = this.getNodeParameter('imagePath', itemIndex) as string;
        // 处理中文路径，确保路径编码正确
        let processedImagePath = imagePath;
        try {
            // 规范化路径分隔符
            processedImagePath = path.normalize(imagePath);
            // 检查文件是否存在
            if (!fs.existsSync(processedImagePath)) {
                throw new NodeOperationError(this.getNode(), `Background image file not found: ${processedImagePath}`);
            }
        } catch (error: any) {
            throw new NodeOperationError(this.getNode(), `Invalid background image path: ${imagePath}. Error: ${error.message}`);
        }
        
        config.canvas = {
            width: 800,
            height: 600,
            backgroundImage: processedImagePath,
            backgroundMode: 'resize'
        };
    }

    const result = await executePythonScript(config);
    return result;
}

async function addText(this: IExecuteFunctions, itemIndex: number, inputData: any): Promise<any> {
    const textSource = this.getNodeParameter('textSource', itemIndex) as string;
    const config: any = {
        mode: 'config',
        canvas: inputData.canvas || {
            width: 800,
            height: 600,
            backgroundColor: '#ffffff'
        },
        elements: inputData.elements || [],
        outputFormat: 'base64'
    };

    if (textSource === 'manual') {
        config.elements.push({
            type: 'text',
            position: [
                this.getNodeParameter('positionX', itemIndex) as number,
                this.getNodeParameter('positionY', itemIndex) as number
            ],
            text: this.getNodeParameter('text', itemIndex) as string,
            fontSize: this.getNodeParameter('fontSize', itemIndex) as number,
            color: this.getNodeParameter('color', itemIndex) as string,
            fontName: this.getNodeParameter('fontName', itemIndex) as string || undefined,
            alignment: this.getNodeParameter('alignment', itemIndex) as string,
        });
    } else {
        // Handle CSV input
        const csvFilePath = this.getNodeParameter('csvFilePath', itemIndex) as string;
        // 处理中文路径，确保路径编码正确
        let processedCsvFilePath = csvFilePath;
        try {
            // 规范化路径分隔符
            processedCsvFilePath = path.normalize(csvFilePath);
            // 检查文件是否存在
            if (!fs.existsSync(processedCsvFilePath)) {
                throw new NodeOperationError(this.getNode(), `CSV file not found: ${processedCsvFilePath}`);
            }
        } catch (error: any) {
            throw new NodeOperationError(this.getNode(), `Invalid CSV file path: ${csvFilePath}. Error: ${error.message}`);
        }
        
        const csvElements = await parseCsvFile(processedCsvFilePath);
        config.elements.push(...csvElements);
    }

    const result = await executePythonScript(config);
    return result;
}

async function addImage(this: IExecuteFunctions, itemIndex: number, inputData: any): Promise<any> {
    const config: any = {
        mode: 'config',
        canvas: inputData.canvas || {
            width: 800,
            height: 600,
            backgroundColor: '#ffffff'
        },
        elements: inputData.elements || [],
        outputFormat: 'base64'
    };

    const overlayImagePath = this.getNodeParameter('overlayImagePath', itemIndex) as string;
    // 处理中文路径，确保路径编码正确
    let processedOverlayImagePath = overlayImagePath;
    try {
        // 规范化路径分隔符
        processedOverlayImagePath = path.normalize(overlayImagePath);
        // 检查文件是否存在
        if (!fs.existsSync(processedOverlayImagePath)) {
            throw new NodeOperationError(this.getNode(), `Overlay image file not found: ${processedOverlayImagePath}`);
        }
    } catch (error: any) {
        throw new NodeOperationError(this.getNode(), `Invalid overlay image path: ${overlayImagePath}. Error: ${error.message}`);
    }

    config.elements.push({
        type: 'image',
        position: [
            this.getNodeParameter('imagePositionX', itemIndex) as number,
            this.getNodeParameter('imagePositionY', itemIndex) as number
        ],
        imagePath: processedOverlayImagePath,
        scale: this.getNodeParameter('scale', itemIndex) as number,
        rotation: this.getNodeParameter('rotation', itemIndex) as number,
    });

    const result = await executePythonScript(config);
    return result;
}

async function parseCsvFile(filePath: string): Promise<any[]> {
    return new Promise((resolve, reject) => {
        const elements: any[] = [];
        
        require('fs').createReadStream(filePath)
            .pipe(csvParser({
                headers: ['text', 'position_x', 'position_y', 'font_size', 'color', 'font_name', 'alignment', 'rotation', 'opacity']
            }))
            .on('data', (row: any) => {
                elements.push({
                    type: 'text',
                    position: [
                        parseInt(row.position_x) || 0,
                        parseInt(row.position_y) || 0
                    ],
                    text: row.text || '',
                    fontSize: parseInt(row.font_size) || 24,
                    color: row.color || '#000000',
                    fontName: row.font_name || undefined,
                    alignment: row.alignment || 'left',
                    rotation: parseFloat(row.rotation) || 0,
                    opacity: parseInt(row.opacity) || 255
                });
            })
            .on('end', () => {
                resolve(elements);
            })
            .on('error', (error: any) => {
                reject(error);
            });
    });
}

async function executePythonScript(config: any): Promise<any> {
    return new Promise((resolve, reject) => {
        // 查找 Python 脚本的多种可能路径
        const possiblePaths = [
            // 开发环境路径
            path.join(__dirname, '..', '..', 'python', 'wrapper.py'),
            // 打包后在 dist 目录中的路径
            path.join(__dirname, '..', 'python', 'wrapper.py'),
            // 全局安装路径
            path.join(__dirname, '..', '..', '..', 'python', 'wrapper.py')
        ];

        let pythonScriptPath = '';
        for (const possiblePath of possiblePaths) {
            if (require('fs').existsSync(possiblePath)) {
                pythonScriptPath = possiblePath;
                break;
            }
        }

        // 如果所有路径都找不到，尝试使用 require.resolve
        if (!pythonScriptPath) {
            try {
                const moduleRoot = path.dirname(require.resolve('n8n-nodes-picEdit'));
                const resolvedPath = path.join(moduleRoot, 'python', 'wrapper.py');
                if (require('fs').existsSync(resolvedPath)) {
                    pythonScriptPath = resolvedPath;
                }
            } catch (e) {
                // 如果 resolve 失败则继续使用空路径
            }
        }

        // 如果仍然找不到脚本文件，则报错
        if (!pythonScriptPath || !require('fs').existsSync(pythonScriptPath)) {
            reject(new Error(`Could not find Python script file. Searched paths: ${possiblePaths.join(', ')}`));
            return;
        }

        const pythonProcess = spawn('python', [pythonScriptPath], {
            stdio: ['pipe', 'pipe', 'pipe']
        });
        
        let stdoutData = '';
        let stderrData = '';
        
        pythonProcess.stdout.on('data', (data) => {
            stdoutData += data.toString('utf8');
        });
        
        pythonProcess.stderr.on('data', (data) => {
            stderrData += data.toString('utf8');
        });
        
        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                reject(new Error("Python script exited with code " + code + ". Stderr: " + stderrData));
                return;
            }
            
            try {
                // 清理可能的编码问题
                let cleanedStdout = stdoutData;
                
                // 移除可能的BOM和控制字符
                cleanedStdout = cleanedStdout.replace(/^\uFEFF/, ''); // 移除BOM
                cleanedStdout = cleanedStdout.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, ''); // 移除控制字符
                
                // 尝试解析JSON
                const result = JSON.parse(cleanedStdout);
                resolve(result);
            } catch (error) {
                // 如果解析失败，尝试清理stderr中的编码问题
                let cleanedStderr = stderrData;
                try {
                    // 尝试修复常见的编码问题
                    cleanedStderr = cleanedStderr.replace(/\\\\+/g, '\\');
                    cleanedStderr = cleanedStderr.replace(/[\uFFFD]/g, '?'); // 替换替换字符
                } catch (e) {
                    // 如果清理失败，使用原始数据
                }
                
                reject(new Error("Failed to parse Python script output: " + stdoutData + (cleanedStderr ? "\nStderr: " + cleanedStderr : "")));
            }
        });
        
        pythonProcess.on('error', (error) => {
            reject(new Error("Failed to start Python process: " + error.message));
        });
        
        // Send config to Python script with proper encoding
        const configJson = JSON.stringify(config);
        pythonProcess.stdin.write(configJson, 'utf8');
        pythonProcess.stdin.end();
    });
}