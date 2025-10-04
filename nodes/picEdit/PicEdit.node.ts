 import { IExecuteFunctions } from 'n8n-workflow';
import { INodeExecutionData, INodeType, INodeTypeDescription, NodeExecutionWithMetadata, NodeOperationError } from 'n8n-workflow';
import * as path from 'path';
import * as fs from 'fs';
import csvParser = require('csv-parser');
const sharp = require('sharp');
const mimeTypes = require('mime-types');
const { v4: uuidv4 } = require('uuid');
import { SharpImageProcessor, CanvasConfig, TextConfig } from './SharpImageProcessor';



export class PicEdit implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Pic Edit',
        name: 'picEdit',
        icon: 'file:picEdit.svg',
        group: ['transform'],
        version: 1,
        subtitle: '={{$parameter["operation"]}}',
        description: 'Generate images with text and image overlays',
        defaults: {
            name: 'PicEdit',
        },
        inputs: ['main'],
        outputs: ['main'],
        credentials: [],
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
            {
                displayName: 'Output Format',
                name: 'outputFormat',
                type: 'options',
                options: [
                    {
                        name: 'PNG',
                        value: 'png',
                    },
                    {
                        name: 'JPEG',
                        value: 'jpeg',
                    },
                    {
                        name: 'WEBP',
                        value: 'webp',
                    },
                ],
                default: 'png',
                description: 'Output image format',
            },
            {
                displayName: 'Quality',
                name: 'quality',
                type: 'number',
                displayOptions: {
                    show: {
                        outputFormat: [
                            'jpeg',
                            'webp',
                        ],
                    },
                },
                typeOptions: {
                    minValue: 1,
                    maxValue: 100,
                },
                default: 90,
                description: 'Image quality (1-100)',
            },
            {
                displayName: 'Field Name',
                name: 'fieldName',
                type: 'string',
                default: 'data',
                description: 'Name of the field in the binary output',
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
                description: 'Path to the background image file (relative paths recommended)',
                placeholder: './images/background.jpg',
            },

            {
                displayName: 'Input Binary Field Name',
                name: 'inputBinaryField',
                type: 'string',
                displayOptions: {
                    show: {
                        operation: [
                            'addText',
                        ],
                    },
                },
                default: '',
                description: 'Name of the binary field containing the input image (leave empty to use JSON canvas data)',
            },
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
                displayName: 'Rotation',
                name: 'rotationAngle',
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
                    minValue: -360,
                    maxValue: 360,
                },
                default: 0,
                description: 'Text rotation angle in degrees',
            },
            {
                displayName: 'Opacity',
                name: 'opacity',
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
                    minValue: 0,
                    maxValue: 255,
                },
                default: 255,
                description: 'Text opacity (0-255, where 255 is fully opaque)',
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
                description: 'Path to the CSV file containing text data (relative paths recommended)',
                placeholder: './data/text_config.csv',
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
                description: 'CSV format: text,position_x,position_y,font_size,color,font_name,rotation,opacity. First row should contain headers.',
            },

            // Add Image
            {
                displayName: 'Input Binary Field Name',
                name: 'inputBinaryField',
                type: 'string',
                displayOptions: {
                    show: {
                        operation: [
                            'addImage',
                        ],
                    },
                },
                default: '',
                description: 'Name of the binary field containing the input image (leave empty to use JSON canvas data)',
            },
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
                description: 'Path to the image file to overlay (relative paths recommended)',
                placeholder: './images/overlay.png',
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

                const binaryResult = await convertToBinary.call(this, i, result);
                const fieldName = this.getNodeParameter('fieldName', i) as string;

                const finalItem: INodeExecutionData = {
                    json: {
                        success: true,
                        message: result?.message || 'Canvas created and converted to binary successfully',
                        fileInfo: binaryResult.fileInfo,
                        debug: result?.debug || undefined
                    },
                    binary: {
                        [fieldName]: {
                            data: binaryResult.buffer.toString('base64'),
                            mimeType: binaryResult.fileInfo.mimeType,
                            fileName: binaryResult.fileInfo.fileName,
                            fileExtension: binaryResult.fileInfo.fileExtension,
                            fileSize: binaryResult.fileInfo.fileSize
                        }
                    }
                };

                returnItems.push(finalItem);
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
    const processor = new SharpImageProcessor();
    
    let canvasConfig: CanvasConfig;

    if (canvasType === 'blank') {
        canvasConfig = {
            width: this.getNodeParameter('width', itemIndex) as number,
            height: this.getNodeParameter('height', itemIndex) as number,
            backgroundColor: this.getNodeParameter('backgroundColor', itemIndex) as string,
        };
    } else {
        const imagePath = this.getNodeParameter('imagePath', itemIndex) as string;
        
        // Validate file path for security
        if (!isValidFilePath(imagePath)) {
            throw new NodeOperationError(this.getNode(), `Invalid or potentially unsafe file path: ${imagePath}`);
        }
        
        let imageBuffer: Buffer;
        let imageMetadata: any;
        try {
            if (!fs.existsSync(imagePath)) {
                throw new NodeOperationError(this.getNode(), `Background image file not found: ${imagePath}`);
            }
            
            const stats = fs.statSync(imagePath);
            if (stats.isDirectory()) {
                throw new NodeOperationError(this.getNode(), `Path is a directory, not a file: ${imagePath}`);
            }
            if (!stats.isFile()) {
                throw new NodeOperationError(this.getNode(), `Path does not point to a regular file: ${imagePath}`);
            }
            
            imageBuffer = fs.readFileSync(imagePath);
            imageMetadata = await sharp(imageBuffer).metadata();
        } catch (error: any) {
            throw new NodeOperationError(this.getNode(), `Unable to read background image file: ${imagePath}. Error: ${error.message}`);
        }
        
        canvasConfig = {
            width: imageMetadata.width || 800,
            height: imageMetadata.height || 600,
            backgroundImageData: imageBuffer.toString('base64'),
        };
    }

    try {
        const canvasBuffer = await processor.createCanvas(canvasConfig);
        
        return {
            success: true,
            base64: canvasBuffer.toString('base64'),
            message: 'Canvas created successfully',
            canvas: canvasConfig,
            elements: []
        };
    } catch (error: any) {
        throw new NodeOperationError(this.getNode(), `Canvas creation failed: ${error.message}`);
    }
}

async function addText(this: IExecuteFunctions, itemIndex: number, inputData: any): Promise<any> {
    const inputBinaryField = this.getNodeParameter('inputBinaryField', itemIndex) as string;
    const textSource = this.getNodeParameter('textSource', itemIndex) as string;
    const processor = new SharpImageProcessor();
    
    let canvasBuffer: Buffer;

    if (inputBinaryField && inputBinaryField.trim() !== '') {
        const items = this.getInputData();
        const currentItem = items[itemIndex];
        
        if (!currentItem.binary || !currentItem.binary[inputBinaryField]) {
            throw new NodeOperationError(this.getNode(), `Binary field '${inputBinaryField}' not found in input data`);
        }
        
        const binaryData = currentItem.binary[inputBinaryField];
        canvasBuffer = Buffer.from(binaryData.data, 'base64');
        
    } else if (inputData.base64) {
        canvasBuffer = Buffer.from(inputData.base64, 'base64');
    } else {
        throw new NodeOperationError(this.getNode(), 'No input canvas found. Please provide either binary field or canvas data from previous step.');
    }

    try {
        let resultBuffer = canvasBuffer;
        
        if (textSource === 'manual') {
            const fontName = this.getNodeParameter('fontName', itemIndex) as string;
            const textConfig: TextConfig = {
                text: this.getNodeParameter('text', itemIndex) as string,
                fontSize: this.getNodeParameter('fontSize', itemIndex) as number,
                color: this.getNodeParameter('color', itemIndex) as string,
                position: [
                    this.getNodeParameter('positionX', itemIndex) as number,
                    this.getNodeParameter('positionY', itemIndex) as number
                ],
                rotation: this.getNodeParameter('rotationAngle', itemIndex) as number,
                opacity: this.getNodeParameter('opacity', itemIndex) as number,
                fontPath: fontName ? fontName : undefined,
            };
            
            resultBuffer = await processor.addText(resultBuffer, textConfig);
        } else {
            const csvFilePath = this.getNodeParameter('csvFilePath', itemIndex) as string;
            
            // Validate file path for security
            if (!isValidFilePath(csvFilePath)) {
                throw new NodeOperationError(this.getNode(), `Invalid or potentially unsafe CSV file path: ${csvFilePath}`);
            }
            
            let processedCsvFilePath = csvFilePath;
            try {
                processedCsvFilePath = path.normalize(csvFilePath).replace(/\\/g, '/');
                if (!fs.existsSync(processedCsvFilePath) && !fs.existsSync(csvFilePath)) {
                    throw new NodeOperationError(this.getNode(), `CSV file not found: ${processedCsvFilePath}`);
                }
                if (!fs.existsSync(processedCsvFilePath)) {
                    processedCsvFilePath = csvFilePath;
                }
                
                const stats = fs.statSync(processedCsvFilePath);
                if (stats.isDirectory()) {
                    throw new NodeOperationError(this.getNode(), `Path is a directory, not a file: ${processedCsvFilePath}`);
                }
                if (!stats.isFile()) {
                    throw new NodeOperationError(this.getNode(), `Path does not point to a regular file: ${processedCsvFilePath}`);
                }
            } catch (error: any) {
                throw new NodeOperationError(this.getNode(), `Invalid CSV file path: ${csvFilePath}. Error: ${error.message}`);
            }
            
            const csvElements = await parseCsvFile(processedCsvFilePath);
            
            // Add each text element from CSV
            for (const element of csvElements) {
                const textConfig: TextConfig = {
                    text: element.text,
                    fontSize: element.fontSize,
                    color: element.color,
                    position: element.position,
                    rotation: element.rotation,
                    opacity: element.opacity,
                    fontPath: element.fontName ? element.fontName : undefined,
                };
                
                resultBuffer = await processor.addText(resultBuffer, textConfig);
            }
        }
        
        return {
            success: true,
            base64: resultBuffer.toString('base64'),
            message: 'Text added successfully'
        };
        
    } catch (error: any) {
        throw new NodeOperationError(this.getNode(), `Text rendering failed: ${error.message}`);
    }
}

async function addImage(this: IExecuteFunctions, itemIndex: number, inputData: any): Promise<any> {
    const inputBinaryField = this.getNodeParameter('inputBinaryField', itemIndex) as string;
    
    let canvasBuffer: Buffer;

    if (inputBinaryField && inputBinaryField.trim() !== '') {
        const items = this.getInputData();
        const currentItem = items[itemIndex];
        
        if (!currentItem.binary || !currentItem.binary[inputBinaryField]) {
            throw new NodeOperationError(this.getNode(), `Binary field '${inputBinaryField}' not found in input data`);
        }
        
        const binaryData = currentItem.binary[inputBinaryField];
        canvasBuffer = Buffer.from(binaryData.data, 'base64');
        
    } else if (inputData.base64) {
        canvasBuffer = Buffer.from(inputData.base64, 'base64');
    } else {
        throw new NodeOperationError(this.getNode(), 'No input canvas found. Please provide either binary field or canvas data from previous step.');
    }

    const overlayImagePath = this.getNodeParameter('overlayImagePath', itemIndex) as string;
    
    // Validate file path for security
    if (!isValidFilePath(overlayImagePath)) {
        throw new NodeOperationError(this.getNode(), `Invalid or potentially unsafe overlay image path: ${overlayImagePath}`);
    }
    
    let overlayImageBuffer: Buffer;
    try {
        if (!fs.existsSync(overlayImagePath)) {
            throw new NodeOperationError(this.getNode(), `Overlay image file not found: ${overlayImagePath}`);
        }
        if (!fs.statSync(overlayImagePath).isFile()) {
            throw new NodeOperationError(this.getNode(), `Path is not a file: ${overlayImagePath}`);
        }
        
        overlayImageBuffer = fs.readFileSync(overlayImagePath);
    } catch (error: any) {
        throw new NodeOperationError(this.getNode(), `Unable to read overlay image file: ${overlayImagePath}. Error: ${error.message}`);
    }

    try {
        const position = [
            this.getNodeParameter('imagePositionX', itemIndex) as number,
            this.getNodeParameter('imagePositionY', itemIndex) as number
        ];
        const scale = this.getNodeParameter('scale', itemIndex) as number;
        const rotation = this.getNodeParameter('rotation', itemIndex) as number;
        
        // Process overlay image with Sharp
        let processedOverlay = sharp(overlayImageBuffer);
        
        if (scale !== 1) {
            const metadata = await processedOverlay.metadata();
            const newWidth = Math.round((metadata.width || 100) * scale);
            const newHeight = Math.round((metadata.height || 100) * scale);
            processedOverlay = processedOverlay.resize(newWidth, newHeight);
        }
        
        if (rotation !== 0) {
            processedOverlay = processedOverlay.rotate(rotation);
        }
        
        const overlayBuffer = await processedOverlay.png().toBuffer();
        
        // Composite overlay onto canvas
        const resultBuffer = await sharp(canvasBuffer)
            .composite([{
                input: overlayBuffer,
                top: position[1],
                left: position[0],
                blend: 'over'
            }])
            .png()
            .toBuffer();
        
        return {
            success: true,
            base64: resultBuffer.toString('base64'),
            message: 'Image added successfully'
        };
        
    } catch (error: any) {
        throw new NodeOperationError(this.getNode(), `Image overlay failed: ${error.message}`);
    }
}

async function parseCsvFile(filePath: string): Promise<any[]> {
    return new Promise((resolve, reject) => {
        const elements: any[] = [];
        
        require('fs').createReadStream(filePath, { encoding: 'utf8' })
            .pipe(csvParser())
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



function generateFileName(extension: string): string {
    const part1 = generateRandomString(13, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ');
    const part2 = generateRandomString(14, 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789');
    return `${part1}-${part2}.${extension}`;
}

function generateRandomString(length: number, chars: string): string {
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

/**
 * Validates file path for security purposes
 * Prevents directory traversal and restricts to safe paths
 */
function isValidFilePath(filePath: string): boolean {
    if (!filePath || typeof filePath !== 'string') {
        return false;
    }
    
    // Normalize the path
    const normalizedPath = path.normalize(filePath);
    
    // Check for directory traversal attempts
    if (normalizedPath.includes('..') || normalizedPath.includes('~')) {
        return false;
    }
    
    // Check for absolute paths to system directories (basic protection)
    const dangerousPaths = [
        '/etc/',
        '/bin/',
        '/sbin/',
        '/usr/bin/',
        '/usr/sbin/',
        '/root/',
        'C:\\Windows\\',
        'C:\\Program Files\\',
        'C:\\Users\\Administrator\\',
        'C:\\Users\\Default\\'
    ];
    
    const upperPath = normalizedPath.toUpperCase();
    for (const dangerous of dangerousPaths) {
        if (upperPath.startsWith(dangerous.toUpperCase())) {
            return false;
        }
    }
    
    // Allow relative paths and safe absolute paths
    return true;
}

async function convertToBinary(this: IExecuteFunctions, itemIndex: number, canvasResult: any): Promise<any> {
    const outputFormat = this.getNodeParameter('outputFormat', itemIndex, 'png') as string;
    const quality = this.getNodeParameter('quality', itemIndex, 90) as number;

    if (!canvasResult || !canvasResult.success) {
        const errorMsg = `No image data available for binary conversion. Canvas result: ${JSON.stringify(canvasResult, null, 2)}`;
        throw new NodeOperationError(this.getNode(), errorMsg);
    }

    if (!canvasResult.base64) {
        const errorMsg = `No base64 image data returned from Python script. Canvas result: ${JSON.stringify(canvasResult, null, 2)}`;
        throw new NodeOperationError(this.getNode(), errorMsg);
    }

    if (typeof canvasResult.base64 !== 'string' || canvasResult.base64.length < 100) {
        const errorMsg = `Invalid base64 data: type=${typeof canvasResult.base64}, length=${canvasResult.base64?.length || 0}`;
        throw new NodeOperationError(this.getNode(), errorMsg);
    }

    let imageBuffer: Buffer;
    try {
        imageBuffer = Buffer.from(canvasResult.base64, 'base64');
        
        if (imageBuffer.length < 100) {
            throw new Error(`Image buffer too small: ${imageBuffer.length} bytes`);
        }
        
    } catch (error: any) {
        const errorMsg = `Failed to convert base64 to buffer: ${error.message}`;
        throw new NodeOperationError(this.getNode(), errorMsg);
    }
    
    let processedBuffer: Buffer;
    let mimeType: string;
    let fileExtension: string;

    try {
        const sharpInstance = sharp(imageBuffer);
        
        switch (outputFormat) {
            case 'png':
                processedBuffer = await sharpInstance.png().toBuffer();
                mimeType = 'image/png';
                fileExtension = 'png';
                break;
            case 'jpeg':
                processedBuffer = await sharpInstance.jpeg({ quality }).toBuffer();
                mimeType = 'image/jpeg';
                fileExtension = 'jpg';
                break;
            case 'webp':
                processedBuffer = await sharpInstance.webp({ quality }).toBuffer();
                mimeType = 'image/webp';
                fileExtension = 'webp';
                break;
            default:
                processedBuffer = await sharpInstance.png().toBuffer();
                mimeType = 'image/png';
                fileExtension = 'png';
        }
        
    } catch (error: any) {
        const errorMsg = `Failed to process image with Sharp: ${error.message}`;
        throw new NodeOperationError(this.getNode(), errorMsg);
    }

    const fileName = generateFileName(fileExtension);
    
    let fileSize: string;
    const bytes = processedBuffer.length;
    if (bytes < 1024) {
        fileSize = `${bytes} bytes`;
    } else if (bytes < 1024 * 1024) {
        fileSize = `${(bytes / 1024).toFixed(2)} KB`;
    } else {
        fileSize = `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    }

    const fileInfo = {
        fileName: fileName,
        fileExtension: fileExtension,
        mimeType: mimeType,
        fileSize: fileSize
    };

    return {
        buffer: processedBuffer,
        fileInfo: fileInfo
    };
}