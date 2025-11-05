/**
 * 导出插件示例
 * 
 * 功能：
 * 1. 在章节右键菜单添加"导出"选项
 * 2. 添加导出工作区Tab
 */

import { h, ref } from 'vue'
import { NButton, NSpace, NCard, NSelect } from 'naive-ui'

// 导出工作区组件
const ExportWorkspace = {
  name: 'ExportWorkspace',
  props: {
    workspace: Object,
    chapters: Array
  },
  setup(props) {
    const format = ref('txt')
    const formatOptions = [
      { label: 'TXT', value: 'txt' },
      { label: 'Markdown', value: 'md' },
      { label: 'DOCX', value: 'docx' },
      { label: 'PDF', value: 'pdf' }
    ]
    
    const handleExport = () => {
      console.log('导出格式:', format.value)
      // 实际导出逻辑
      alert(`导出为 ${format.value} 格式`)
    }
    
    return () => h('div', {
      style: {
        padding: '32px 40px',
        height: '100%',
        overflow: 'auto'
      }
    }, [
      h('h2', {
        style: {
          fontSize: '24px',
          fontWeight: '600',
          color: 'rgba(255,255,255,0.95)',
          marginBottom: '24px'
        }
      }, '导出作品'),
      h(NCard, {
        style: {
          background: 'rgba(255,255,255,0.04)',
          border: '1px solid rgba(255,255,255,0.08)',
          marginBottom: '20px'
        }
      }, {
        default: () => [
          h('div', {
            style: {
              marginBottom: '16px',
              fontSize: '14px',
              color: 'rgba(255,255,255,0.7)'
            }
          }, '选择导出格式'),
          h(NSelect, {
            value: format.value,
            'onUpdate:value': (val) => { format.value = val },
            options: formatOptions,
            style: { marginBottom: '16px' }
          }),
          h(NButton, {
            type: 'primary',
            onClick: handleExport
          }, '导出')
        ]
      }),
      h('div', {
        style: {
          fontSize: '13px',
          color: 'rgba(255,255,255,0.5)',
          lineHeight: '1.6'
        }
      }, [
        h('p', '导出信息：'),
        h('ul', {
          style: { paddingLeft: '20px', margin: '8px 0' }
        }, [
          h('li', `工作空间：${props.workspace?.title || 'N/A'}`),
          h('li', `章节数：${props.chapters?.length || 0}`),
          h('li', `总字数：${props.chapters?.reduce((sum, ch) => sum + (ch.content?.length || 0), 0).toLocaleString() || 0}`)
        ])
      ])
    ])
  }
}

// 导出图标
const DownloadIcon = () => h('svg', {
  xmlns: 'http://www.w3.org/2000/svg',
  width: 24,
  height: 24,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  'stroke-width': 2,
  'stroke-linecap': 'round',
  'stroke-linejoin': 'round'
}, [
  h('path', { d: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4' }),
  h('polyline', { points: '7 10 12 15 17 10' }),
  h('line', { x1: 12, y1: 15, x2: 12, y2: 3 })
])

export default {
  name: 'export',
  version: '1.0.0',
  description: '导出作品为多种格式',
  author: 'NovelGen Team',
  
  hooks: {
    // 添加导出工作区Tab
    'workspace.tabs': (context) => {
      return {
        key: 'export',
        label: '导出',
        icon: DownloadIcon,
        component: ExportWorkspace,
        props: {
          workspace: context.workspace,
          chapters: context.chapters
        },
        tooltip: '导出作品',
        order: 95
      }
    },
    
    // 扩展章节右键菜单
    'sidebar.chapter.actions': (context) => {
      return {
        label: '导出此章节',
        key: 'export-chapter',
        handler: (chapter) => {
          console.log('导出章节:', chapter)
          alert(`导出章节 ${chapter.chapter_number}`)
        }
      }
    }
  }
}

